"""
科研与比赛成果相关路由
处理：上传证书 → LLM识别 → 学生确认 → 存入数据库
"""

import shutil
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from ..config import settings
from ..database import get_db
from ..models import Achievement, Student
from ..schemas import (
    AchievementCreate,
    AchievementOut,
    AchievementWithStudent,
    MessageResponse,
    StudentCreate,
    StudentOut,
    UploadResponse,
)
from ..services.llm_service import extract_certificate_info

router = APIRouter()


# ──────────────────────────────────────────────
# 学生注册 / 查询
# ──────────────────────────────────────────────
@router.post("/students", response_model=StudentOut, summary="注册学生")
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """注册新学生，如果学号已存在则返回已有记录"""
    existing = db.query(Student).filter(Student.student_id == student.student_id).first()
    if existing:
        return existing

    db_student = Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.get("/students/{student_id}", response_model=StudentOut, summary="查询学生")
async def get_student(student_id: str, db: Session = Depends(get_db)):
    """根据学号查询学生"""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student


# ──────────────────────────────────────────────
# 上传证书 + LLM 识别
# ──────────────────────────────────────────────
@router.post("/upload", response_model=UploadResponse, summary="上传证书并识别")
async def upload_certificate(file: UploadFile = File(...)):
    """
    步骤1-2：学生上传获奖证书 → 调用 LLM 提取信息
    返回提取结果供学生确认
    """
    # 校验文件类型
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式 {ext}，请上传 {settings.ALLOWED_EXTENSIONS}",
        )

    # 校验文件大小
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"文件大小超过 {settings.MAX_FILE_SIZE_MB}MB 限制")

    # 保存文件
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = Path(settings.UPLOAD_DIR) / filename
    with open(file_path, "wb") as f:
        f.write(content)

    # 调用 LLM 识别
    try:
        extracted, raw_response = await extract_certificate_info(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM 识别失败: {str(e)}")

    return UploadResponse(
        image_path=f"/uploads/{filename}",
        extracted=extracted,
        raw_response=raw_response,
    )


# ──────────────────────────────────────────────
# 学生确认 → 存入数据库
# ──────────────────────────────────────────────
@router.post("/confirm", response_model=AchievementOut, summary="确认并保存成果")
async def confirm_achievement(data: AchievementCreate, db: Session = Depends(get_db)):
    """
    步骤3：学生确认 LLM 提取结果后，将数据存入数据库
    """
    # 检查学生是否存在
    student = db.query(Student).filter(Student.id == data.student_db_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    achievement = Achievement(
        student_db_id=data.student_db_id,
        competition_name=data.competition_name,
        winner_name=data.winner_name,
        award_level=data.award_level,
        award_date=data.award_date,
        category=data.category,
        certificate_image=data.certificate_image,
        status="confirmed",
    )
    db.add(achievement)
    db.commit()
    db.refresh(achievement)
    return achievement


# ──────────────────────────────────────────────
# 查询成果列表
# ──────────────────────────────────────────────
@router.get("/list", response_model=List[AchievementWithStudent], summary="查询成果列表")
async def list_achievements(
    student_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """查询成果列表，支持按学号和状态筛选（包含学生信息）"""
    query = db.query(Achievement).options(joinedload(Achievement.student))

    if student_id:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if student:
            query = query.filter(Achievement.student_db_id == student.id)

    if status:
        query = query.filter(Achievement.status == status)

    return query.order_by(Achievement.created_at.desc()).offset(skip).limit(limit).all()


@router.patch("/{achievement_id}/status", response_model=MessageResponse, summary="更新成果状态")
async def update_status(achievement_id: int, status: str, db: Session = Depends(get_db)):
    """辅导员审核：更新成果状态"""
    if status not in ("confirmed", "rejected", "pending"):
        raise HTTPException(status_code=400, detail="无效状态")

    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if not achievement:
        raise HTTPException(status_code=404, detail="成果记录不存在")

    achievement.status = status
    db.commit()
    return MessageResponse(message=f"状态已更新为 {status}")
