"""
考勤模块路由：花名册导入、课程表管理、一键考勤、签到抽查
"""

import csv
import io
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import (
    AttendanceRecord,
    CheckInLog,
    CheckInSession,
    ClassRoster,
    CourseSchedule,
    LeaveSlip,
    User,
)
from ..schemas import (
    AttendanceRecordCreate,
    AttendanceRecordOut,
    CheckInLogOut,
    CheckInSessionCreate,
    CheckInSessionOut,
    ClassRosterOut,
    CourseScheduleCreate,
    CourseScheduleOut,
    MessageResponse,
)
from ..services.auth_service import get_current_user

router = APIRouter()


def require_monitor_or_counselor(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("monitor", "counselor"):
        raise HTTPException(status_code=403, detail="需要纪律委员或辅导员权限")
    return current_user


# ──────────────────────────────────────────────
# 花名册管理
# ──────────────────────────────────────────────

@router.post("/roster/import", response_model=MessageResponse, summary="导入班级花名册CSV")
async def import_roster(
    file: UploadFile = File(...),
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="请上传 CSV 文件")

    content = await file.read()
    for encoding in ("utf-8-sig", "utf-8", "gbk", "gb2312"):
        try:
            text = content.decode(encoding)
            break
        except (UnicodeDecodeError, LookupError):
            continue
    else:
        raise HTTPException(status_code=400, detail="文件编码不支持，请使用 UTF-8 或 GBK 编码")

    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    header_row_idx = None
    for i, row in enumerate(rows):
        row_lower = ",".join(row).lower()
        if "学号" in row_lower and "姓名" in row_lower:
            header_row_idx = i
            break

    if header_row_idx is None:
        raise HTTPException(status_code=400, detail="未找到表头行（需包含 学号、姓名 列）")

    headers = rows[header_row_idx]
    col_map = {}
    for idx, h in enumerate(headers):
        h_clean = h.strip()
        if "学号" in h_clean:
            col_map["student_id"] = idx
        elif "姓名" in h_clean and "家长" not in h_clean:
            col_map["name"] = idx
        elif "性别" in h_clean:
            col_map["gender"] = idx
        elif "年级专业班级" in h_clean:
            col_map["class_name"] = idx
        elif "所属院系" in h_clean or "二级学院" in h_clean:
            col_map["major"] = idx
        elif "本人" in h_clean and "电话" in h_clean:
            col_map["phone"] = idx
        elif "辅导员" in h_clean:
            col_map["counselor"] = idx

    if "student_id" not in col_map or "name" not in col_map:
        raise HTTPException(status_code=400, detail="CSV 中缺少必要列：学号、姓名")

    imported = 0
    skipped = 0
    for row in rows[header_row_idx + 1:]:
        if len(row) <= col_map["student_id"]:
            continue
        sid = row[col_map["student_id"]].strip()
        name = row[col_map["name"]].strip()
        if not sid or not name:
            continue

        existing = db.query(ClassRoster).filter(ClassRoster.student_id == sid).first()
        if existing:
            skipped += 1
            continue

        roster = ClassRoster(
            student_id=sid,
            name=name,
            gender=row[col_map.get("gender", -1)].strip() if col_map.get("gender") is not None and len(row) > col_map["gender"] else "",
            class_name=row[col_map.get("class_name", -1)].strip() if col_map.get("class_name") is not None and len(row) > col_map["class_name"] else "",
            major=row[col_map.get("major", -1)].strip() if col_map.get("major") is not None and len(row) > col_map["major"] else "",
            phone=row[col_map.get("phone", -1)].strip() if col_map.get("phone") is not None and len(row) > col_map["phone"] else "",
            counselor=row[col_map.get("counselor", -1)].strip() if col_map.get("counselor") is not None and len(row) > col_map["counselor"] else "",
        )
        db.add(roster)
        imported += 1

    db.commit()
    return MessageResponse(message=f"导入成功：新增 {imported} 人，跳过 {skipped} 人（已存在）")


@router.get("/roster", response_model=list[ClassRosterOut], summary="获取花名册")
async def get_roster(
    class_name: str = Query("", description="按班级筛选"),
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    q = db.query(ClassRoster)
    if class_name:
        q = q.filter(ClassRoster.class_name == class_name)
    return q.order_by(ClassRoster.class_name, ClassRoster.student_id).all()


@router.get("/roster/classes", summary="获取所有班级列表")
async def get_classes(
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    roster_classes = db.query(ClassRoster.class_name).distinct().all()
    schedule_classes = db.query(CourseSchedule.class_name).distinct().all()
    all_classes = {r[0] for r in roster_classes if r[0]} | {r[0] for r in schedule_classes if r[0]}
    return {"classes": sorted(all_classes)}


@router.get("/roster/class-size", summary="获取班级人数")
async def get_class_size(
    class_name: str = Query(..., description="班级名称"),
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    count = db.query(ClassRoster).filter(ClassRoster.class_name == class_name).count()
    return {"class_name": class_name, "size": count}


@router.post("/roster/add", response_model=ClassRosterOut, summary="手动添加学生到花名册")
async def add_roster_student(
    student_id: str = Query(..., description="学号"),
    name: str = Query(..., description="姓名"),
    class_name: str = Query(..., description="班级"),
    gender: str = Query("", description="性别"),
    phone: str = Query("", description="电话"),
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    existing = db.query(ClassRoster).filter(ClassRoster.student_id == student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="该学号已存在")
    roster = ClassRoster(
        student_id=student_id,
        name=name,
        class_name=class_name,
        gender=gender,
        phone=phone,
    )
    db.add(roster)
    db.commit()
    db.refresh(roster)
    return roster


@router.put("/roster/{roster_id}", response_model=ClassRosterOut, summary="编辑花名册学生信息")
async def update_roster_student(
    roster_id: int,
    name: str = Query(None, description="姓名"),
    student_id: str = Query(None, description="学号"),
    class_name: str = Query(None, description="班级"),
    gender: str = Query(None, description="性别"),
    phone: str = Query(None, description="电话"),
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    roster = db.query(ClassRoster).filter(ClassRoster.id == roster_id).first()
    if not roster:
        raise HTTPException(status_code=404, detail="学生不存在")
    if name is not None:
        roster.name = name.strip()
    if student_id is not None:
        roster.student_id = student_id.strip()
    if class_name is not None:
        roster.class_name = class_name.strip()
    if gender is not None:
        roster.gender = gender.strip()
    if phone is not None:
        roster.phone = phone.strip()
    db.commit()
    db.refresh(roster)
    return roster


@router.delete("/roster/{roster_id}", response_model=MessageResponse, summary="删除花名册学生")
async def delete_roster_student(
    roster_id: int,
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    roster = db.query(ClassRoster).filter(ClassRoster.id == roster_id).first()
    if not roster:
        raise HTTPException(status_code=404, detail="学生不存在")
    db.delete(roster)
    db.commit()
    return MessageResponse(message="已删除")


# ──────────────────────────────────────────────
# 课程表管理
# ──────────────────────────────────────────────

@router.post("/schedule", response_model=CourseScheduleOut, summary="添加课程")
async def add_schedule(
    data: CourseScheduleCreate,
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    course = CourseSchedule(
        class_name=data.class_name,
        week_number=data.week_number,
        day_of_week=data.day_of_week,
        period=data.period,
        course_name=data.course_name,
        teacher=data.teacher,
        classroom=data.classroom,
        date_str=data.date_str,
        created_by=current_user.id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.post("/schedule/batch", response_model=MessageResponse, summary="批量添加课程（拍课表解��结果）")
async def batch_add_schedule(
    courses: list[CourseScheduleCreate],
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    for data in courses:
        cn = data.class_name.strip()
        dow = data.day_of_week.strip()
        period = data.period.strip()
        existing = db.query(CourseSchedule).filter(
            CourseSchedule.class_name == cn,
            CourseSchedule.week_number == data.week_number,
            CourseSchedule.day_of_week == dow,
            CourseSchedule.period == period,
        ).first()
        if existing:
            existing.course_name = data.course_name.strip()
            existing.teacher = (data.teacher or "").strip()
            existing.classroom = (data.classroom or "").strip()
            existing.date_str = (data.date_str or "").strip()
        else:
            course = CourseSchedule(
                class_name=cn,
                week_number=data.week_number,
                day_of_week=dow,
                period=period,
                course_name=data.course_name.strip(),
                teacher=(data.teacher or "").strip(),
                classroom=(data.classroom or "").strip(),
                date_str=(data.date_str or "").strip(),
                created_by=current_user.id,
            )
            db.add(course)
    db.commit()
    return MessageResponse(message=f"已保存 {len(courses)} 门课程")


@router.get("/schedule", response_model=list[CourseScheduleOut], summary="查询课程表")
async def get_schedule(
    class_name: str = Query(..., description="班级"),
    week_number: int = Query(0, description="教学周数，0=全部"),
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    class_name = class_name.strip()
    q = db.query(CourseSchedule).filter(CourseSchedule.class_name == class_name)
    if week_number > 0:
        q = q.filter(CourseSchedule.week_number == week_number)
    day_order = {"周一": 1, "周二": 2, "周三": 3, "周四": 4, "周五": 5, "周六": 6, "周日": 7}
    results = q.all()

    if not results and week_number > 1:
        week1 = db.query(CourseSchedule).filter(
            CourseSchedule.class_name == class_name,
            CourseSchedule.week_number == 1,
        ).all()
        for c in week1:
            new_course = CourseSchedule(
                class_name=c.class_name,
                week_number=week_number,
                day_of_week=c.day_of_week,
                period=c.period,
                course_name=c.course_name,
                teacher=c.teacher,
                classroom=c.classroom,
                date_str="",
                created_by=current_user.id,
            )
            db.add(new_course)
        if week1:
            db.commit()
            results = db.query(CourseSchedule).filter(
                CourseSchedule.class_name == class_name,
                CourseSchedule.week_number == week_number,
            ).all()

    results.sort(key=lambda c: (c.week_number, day_order.get(c.day_of_week, 0), c.period))
    return results


@router.delete("/schedule/{schedule_id}", response_model=MessageResponse, summary="删除课程")
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    course = db.query(CourseSchedule).filter(CourseSchedule.id == schedule_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    db.delete(course)
    db.commit()
    return MessageResponse(message="已删除")


@router.put("/schedule/{schedule_id}", response_model=CourseScheduleOut, summary="编辑课程")
async def update_schedule(
    schedule_id: int,
    data: CourseScheduleCreate,
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    course = db.query(CourseSchedule).filter(CourseSchedule.id == schedule_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    course.day_of_week = data.day_of_week.strip()
    course.period = data.period.strip()
    course.course_name = data.course_name.strip()
    course.teacher = (data.teacher or "").strip()
    course.classroom = (data.classroom or "").strip()
    course.date_str = (data.date_str or "").strip()
    db.commit()
    db.refresh(course)
    return course


# ──────────────────────────────────────────────
# 假条图片上传
# ──────────────────────────────────────────────

@router.post("/leave-slip/upload", summary="上传假条图片")
async def upload_leave_slip(
    file: UploadFile = File(...),
    current_user: User = Depends(require_monitor_or_counselor),
):
    ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        raise HTTPException(status_code=400, detail="仅支持 jpg/png/webp 图片")

    save_dir = Path(settings.UPLOAD_DIR) / "leave_slips"
    save_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = save_dir / filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return {"image_path": f"/uploads/leave_slips/{filename}"}


@router.post("/classroom-photo/upload", summary="上传教室照片")
async def upload_classroom_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(require_monitor_or_counselor),
):
    ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        raise HTTPException(status_code=400, detail="仅支持 jpg/png/webp 图片")

    save_dir = Path(settings.UPLOAD_DIR) / "classroom_photos"
    save_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = save_dir / filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return {"image_path": f"/uploads/classroom_photos/{filename}"}


# ──────────────────────────────────────────────
# 一键考勤
# ──────────────────────────────────────────────

@router.post("/record", response_model=AttendanceRecordOut, summary="提交考勤记录")
async def create_attendance(
    data: AttendanceRecordCreate,
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    if len(data.classroom_photos) < 2:
        raise HTTPException(status_code=400, detail="请上传至少2张教室照片")

    class_size = data.class_size
    if class_size == 0:
        count = db.query(ClassRoster).filter(ClassRoster.class_name == data.class_name).count()
        class_size = count if count > 0 else data.class_size

    not_arrived = data.sick_leave_count + data.personal_leave_count + data.late_count + data.early_leave_count + data.absent_count
    actual = class_size - not_arrived if class_size > not_arrived else 0

    # 到课率：实到人数 / 班级人数
    rate = f"{round(actual / class_size * 100)}%" if class_size > 0 else "0%"
    # 含请假到课率：(实到 + 病公假) / 班级人数
    present_with_leave = actual + data.sick_leave_count
    rate_with_leave = f"{round(present_with_leave / class_size * 100)}%" if class_size > 0 else "0%"

    record = AttendanceRecord(
        schedule_id=data.schedule_id,
        class_name=data.class_name,
        date_str=data.date_str,
        day_of_week=data.day_of_week,
        period=data.period,
        course_name=data.course_name,
        teacher=data.teacher,
        classroom=data.classroom,
        class_size=class_size,
        actual_count=actual,
        sick_leave_count=data.sick_leave_count,
        personal_leave_count=data.personal_leave_count,
        late_count=data.late_count,
        early_leave_count=data.early_leave_count,
        absent_count=data.absent_count,
        not_arrived_count=not_arrived,
        attendance_rate=rate,
        attendance_rate_with_leave=rate_with_leave,
        leave_details=data.leave_details,
        classroom_photos=json.dumps(data.classroom_photos),
        checker=data.checker or current_user.name,
        week_number=data.week_number,
        created_by=current_user.id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    if data.leave_slips:
        for slip in data.leave_slips:
            leave_slip = LeaveSlip(
                attendance_record_id=record.id,
                student_id=slip.student_id,
                student_name=slip.student_name,
                reason=slip.reason,
                image_path=slip.image_path,
            )
            db.add(leave_slip)
        db.commit()

    return record


@router.get("/records", response_model=list[AttendanceRecordOut], summary="查询考勤记录列表")
async def list_records(
    class_name: str = Query("", description="班级"),
    week_number: int = Query(0, description="周数"),
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    q = db.query(AttendanceRecord)
    if class_name:
        q = q.filter(AttendanceRecord.class_name == class_name)
    if week_number > 0:
        q = q.filter(AttendanceRecord.week_number == week_number)
    return q.order_by(AttendanceRecord.created_at.desc()).all()


@router.get("/records/stats", summary="考勤统计")
async def attendance_stats(
    class_name: str = Query(..., description="班级"),
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    records = db.query(AttendanceRecord).filter(AttendanceRecord.class_name == class_name).all()
    if not records:
        return {"total_records": 0, "avg_rate": "0%", "total_absent": 0, "total_late": 0}

    total = len(records)
    rates = []
    for r in records:
        try:
            rates.append(int(r.attendance_rate.replace("%", "")))
        except (ValueError, AttributeError):
            pass
    avg_rate = f"{round(sum(rates) / len(rates))}%" if rates else "0%"
    total_absent = sum(r.absent_count for r in records)
    total_late = sum(r.late_count for r in records)

    return {
        "total_records": total,
        "avg_rate": avg_rate,
        "total_absent": total_absent,
        "total_late": total_late,
    }


@router.get("/records/export", summary="导出考勤表（CSV，吉利学院格式）")
async def export_records(
    class_name: str = Query("", description="班级筛选"),
    week_number: int = Query(0, description="周数筛选"),
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    q = db.query(AttendanceRecord)
    if class_name:
        q = q.filter(AttendanceRecord.class_name == class_name)
    if week_number > 0:
        q = q.filter(AttendanceRecord.week_number == week_number)
    records = q.order_by(AttendanceRecord.created_at).all()

    output = io.StringIO()
    output.write("﻿")
    writer = csv.writer(output)

    writer.writerow(["吉利学院学风督查记录表（二级学院、辅导员用表）"] + [""] * 18)
    writer.writerow([f"检查人员：{current_user.name}"] + [""] * 18)

    writer.writerow([
        "序号", "学院", "年级专业班级", "时间", "周数", "节次", "教室",
        "课程名称", "授课教师", "辅导员",
        "班级人数", "实到人数", "病公假人数", "事假人数", "迟到人数", "早退人数", "旷课人数", "未到人数",
        "平均到课率", "平均到课率（含病公假）",
        "请假、违纪情况说明",
    ])

    for i, r in enumerate(records, 1):
        writer.writerow([
            i,
            "",
            r.class_name,
            r.date_str,
            f"第{r.week_number}周" if r.week_number else "",
            r.period,
            r.classroom,
            r.course_name,
            r.teacher,
            r.checker,
            r.class_size,
            r.actual_count,
            r.sick_leave_count,
            r.personal_leave_count,
            r.late_count,
            r.early_leave_count,
            r.absent_count,
            r.not_arrived_count,
            r.attendance_rate,
            r.attendance_rate_with_leave,
            r.leave_details or "",
        ])

    output.seek(0)
    filename = f"考勤记录_{class_name or '全部'}_{datetime.now().strftime('%Y%m%d')}.csv"
    encoded_filename = quote(filename)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
    )


# ──────────────────────────────────────────────
# 签到抽查（二维码签到）
# ──────────────────────────────────────────────

@router.post("/checkin/create", response_model=CheckInSessionOut, summary="创建签到会话（生成二维码）")
async def create_checkin(
    data: CheckInSessionCreate,
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    code = uuid.uuid4().hex[:8]
    session = CheckInSession(
        code=code,
        class_name=data.class_name,
        course_name=data.course_name,
        expire_minutes=data.expire_minutes,
        schedule_id=data.schedule_id,
        created_by=current_user.id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return CheckInSessionOut(
        id=session.id,
        code=session.code,
        class_name=session.class_name,
        course_name=session.course_name,
        expire_minutes=session.expire_minutes,
        is_active=session.is_active,
        created_at=session.created_at,
        log_count=0,
    )


@router.post("/checkin/{code}", response_model=MessageResponse, summary="学生扫码签到")
async def do_checkin(
    code: str,
    status: str = Query("正常", description="签到状态"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(CheckInSession).filter(CheckInSession.code == code).first()
    if not session:
        raise HTTPException(status_code=404, detail="签到码无效")
    if not session.is_active:
        raise HTTPException(status_code=400, detail="签到已结束")

    expire_at = session.created_at + timedelta(minutes=session.expire_minutes)
    if datetime.utcnow() > expire_at:
        session.is_active = False
        db.commit()
        raise HTTPException(status_code=400, detail="签到已过期")

    existing = db.query(CheckInLog).filter(
        CheckInLog.session_id == session.id,
        CheckInLog.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="你已经签到过了")

    log = CheckInLog(
        session_id=session.id,
        user_id=current_user.id,
        student_name=current_user.name,
        student_number=current_user.username,
        status=status,
    )
    db.add(log)
    db.commit()
    return MessageResponse(message=f"签到成功！{current_user.name}")


@router.get("/checkin/{code}/status", summary="查询签到状态")
async def checkin_status(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(CheckInSession).filter(CheckInSession.code == code).first()
    if not session:
        raise HTTPException(status_code=404, detail="签到码无效")

    expire_at = session.created_at + timedelta(minutes=session.expire_minutes)
    if datetime.utcnow() > expire_at and session.is_active:
        session.is_active = False
        db.commit()

    logs = db.query(CheckInLog).filter(CheckInLog.session_id == session.id).order_by(CheckInLog.checked_at).all()

    roster_count = db.query(ClassRoster).filter(ClassRoster.class_name == session.class_name).count()

    checked_ids = {log.student_number for log in logs}
    roster_students = db.query(ClassRoster).filter(ClassRoster.class_name == session.class_name).all()
    not_checked = [{"student_id": s.student_id, "name": s.name} for s in roster_students if s.student_id not in checked_ids]

    return {
        "session": {
            "id": session.id,
            "code": session.code,
            "class_name": session.class_name,
            "course_name": session.course_name,
            "is_active": session.is_active,
            "expire_minutes": session.expire_minutes,
            "created_at": session.created_at.isoformat(),
        },
        "checked_count": len(logs),
        "roster_count": roster_count,
        "checked_list": [CheckInLogOut.model_validate(l) for l in logs],
        "not_checked_list": not_checked,
    }


@router.post("/checkin/{code}/close", response_model=MessageResponse, summary="关闭签到")
async def close_checkin(
    code: str,
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    session = db.query(CheckInSession).filter(CheckInSession.code == code).first()
    if not session:
        raise HTTPException(status_code=404, detail="签到码无效")
    session.is_active = False
    db.commit()
    return MessageResponse(message="签到已关闭")


@router.get("/checkin-sessions", summary="获取签到会话列表")
async def list_checkin_sessions(
    class_name: str = Query("", description="班级筛选"),
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    q = db.query(CheckInSession)
    if class_name:
        q = q.filter(CheckInSession.class_name == class_name)
    sessions = q.order_by(CheckInSession.created_at.desc()).limit(50).all()

    result = []
    for s in sessions:
        log_count = db.query(CheckInLog).filter(CheckInLog.session_id == s.id).count()
        result.append(CheckInSessionOut(
            id=s.id,
            code=s.code,
            class_name=s.class_name,
            course_name=s.course_name,
            expire_minutes=s.expire_minutes,
            is_active=s.is_active,
            created_at=s.created_at,
            log_count=log_count,
        ))
    return result


# ──────────────────────────────────────────────
# 课表图片识别（拍课表）
# ──────────────────────────────────────────────

@router.post("/schedule/parse-image", summary="拍课表识别（上传图片，LLM解析）")
async def parse_schedule_image(
    file: UploadFile = File(...),
    class_name: str = Query(..., description="班级名称"),
    week_number: int = Query(..., description="教学周数"),
    current_user: User = Depends(require_monitor_or_counselor),
    db: Session = Depends(get_db),
):
    import base64
    import json

    from ..config import settings
    from ..services.llm_service import call_llm_with_image

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")

    image_bytes = await file.read()
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    mime = file.content_type or "image/jpeg"

    prompt = f"""你是课程表识别专家。请仔细分析这张课程表图片，精确提取每一门课程的信息。

【课表布局说明】
这是一张大学教务系统的课程表，典型结构如下：
- 最左列是节次编号和上课时间（第1节、第2节...或第1-2节等）
- 顶部横向标题是：星期一、星期二、星期三、星期四、星期五（可能还有星期六、星期日）
- 每个单元格内可能包含：课程名称、教师姓名、周次范围（如1-16周）、教室地点
- 有些课程跨多个节次（合并单元格），比如占了第1-2节的位置

【最关键规则 — 星期判断】
- 课程属于哪个星期，完全取决于它在哪一【列】
- 从左到右，第一个数据列=星期一，第二个=星期二，以此类推
- 绝对不要把不同列的课程混淆到同一天
- 如果某列是空的，说明那天没有对应节次的课

【周次过滤】
- 单元格内可能写着周次范围如"1-16周"、"1-8周"、"9-16周"
- 当前是第{week_number}周，请只提取周次范围包含第{week_number}周的课程
- 如果看不清周次范围，就默认包含

【上下文信息】
班级：{class_name}
教学周数：第{week_number}周

【输出格式】
返回 JSON 数组，每门课程包含：
- day_of_week: 星期几（必须转换为：周一、周二、周三、周四、周五、周六、周日）
- period: 节次（如 "1-2", "3-4", "5-6", "7-8", "9-10"，根据课程占据的节次行来判断）
- course_name: 课程名称（只要课程名，不要周次、教室等附加信息）
- teacher: 授课教师（识别不到就留空字符串）
- classroom: 教室/地点（识别不到就留空字符串）

只返回 JSON 数组，不要任何其他文字。"""

    if not settings.OPENAI_API_KEY and settings.LLM_PROVIDER == "openai":
        raise HTTPException(status_code=500, detail="未配置 LLM API Key，请在 .env 文件中设置 OPENAI_API_KEY")
    if not settings.GEMINI_API_KEY and settings.LLM_PROVIDER == "gemini":
        raise HTTPException(status_code=500, detail="未配置 Gemini API Key，请在 .env 文件中设置 GEMINI_API_KEY")

    try:
        raw = await call_llm_with_image(b64, mime, prompt)
        raw_clean = raw.strip()
        if "</think>" in raw_clean:
            raw_clean = raw_clean.split("</think>")[-1].strip()
        if raw_clean.startswith("```"):
            raw_clean = raw_clean.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        courses = json.loads(raw_clean)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"课表识别失败: {str(e)}")

    result = []
    for c in courses:
        result.append({
            "class_name": class_name,
            "week_number": week_number,
            "day_of_week": c.get("day_of_week", ""),
            "period": c.get("period", ""),
            "course_name": c.get("course_name", ""),
            "teacher": c.get("teacher", ""),
            "classroom": c.get("classroom", ""),
            "date_str": "",
        })

    return {"courses": result, "raw_response": raw}
