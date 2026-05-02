"""
科研与比赛成果相关路由
支持 4 类成果：科研项目、专利软著、学术论文、学科竞赛
处理：上传证书 → LLM识别 → 学生确认 → 存入数据库
"""

import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session, joinedload

from ..config import settings
from ..database import get_db
from ..models import Competition, Paper, Patent, ResearchProject, Student
from ..schemas import (
    CompetitionCreate,
    CompetitionWithStudent,
    MessageResponse,
    PaperCreate,
    PaperWithStudent,
    PatentCreate,
    PatentWithStudent,
    ResearchProjectCreate,
    ResearchProjectWithStudent,
    StudentCreate,
    StudentOut,
    UploadResponse,
)
from ..services.llm_service import extract_certificate_info

router = APIRouter()

CATEGORY_MODELS = {
    "科研项目": ResearchProject,
    "专利软著": Patent,
    "学术论文": Paper,
    "学科竞赛": Competition,
}

CATEGORY_SCHEMAS = {
    "科研项目": ResearchProjectCreate,
    "专利软著": PatentCreate,
    "学术论文": PaperCreate,
    "学科竞赛": CompetitionCreate,
}

VALID_CATEGORIES = list(CATEGORY_MODELS.keys())


# ──────────────────────────────────────────────
# 学生注册 / 查询
# ──────────────────────────────────────────────
@router.post("/students", response_model=StudentOut, summary="注册学生")
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
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
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student


# ──────────────────────────────────────────────
# 上传证书 + LLM 识别（带 category 参数）
# ──────────────────────────────────────────────
@router.post("/upload", response_model=UploadResponse, summary="上传证书并识别")
async def upload_certificate(
    category: str = Query(..., description="成果类别：科研项目/专利软著/学术论文/学科竞赛"),
    file: UploadFile = File(...),
):
    if category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"无效类别，必须为 {VALID_CATEGORIES} 之一")

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式 {ext}，请上传 {settings.ALLOWED_EXTENSIONS}",
        )

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"文件大��超过 {settings.MAX_FILE_SIZE_MB}MB 限制")

    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = Path(settings.UPLOAD_DIR) / filename
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        extracted, raw_response = await extract_certificate_info(file_path, category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM 识别失败: {str(e)}")

    return UploadResponse(
        image_path=f"/uploads/{filename}",
        category=category,
        extracted=extracted.model_dump(),
        raw_response=raw_response,
    )


# ──────────────────────────────────────────────
# 学生确认 → 存入对应的表
# ──────────────────────────────────────────────
@router.post("/confirm/{category}", response_model=dict, summary="确认并保存成果")
async def confirm_achievement(category: str, data: dict, db: Session = Depends(get_db)):
    if category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"无效类别，必须为 {VALID_CATEGORIES} 之一")

    student_db_id = data.get("student_db_id")
    if not student_db_id:
        raise HTTPException(status_code=400, detail="缺少 student_db_id")

    student = db.query(Student).filter(Student.id == student_db_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    model_cls = CATEGORY_MODELS[category]
    schema_cls = CATEGORY_SCHEMAS[category]

    try:
        validated = schema_cls(**data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"数据验证失败: {str(e)}")

    record = model_cls(**validated.model_dump())
    record.status = "confirmed"
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"id": record.id, "message": "提交成功"}


# ──────────────────────────────────────────────
# 查询成果列表（按类别）
# ──────────────────────────────────────────────
@router.get("/list/{category}", summary="查询成果列表")
async def list_achievements(
    category: str,
    student_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    if category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"无效类别，必须为 {VALID_CATEGORIES} 之一")

    model_cls = CATEGORY_MODELS[category]
    query = db.query(model_cls).options(joinedload(model_cls.student))

    if student_id:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if student:
            query = query.filter(model_cls.student_db_id == student.id)
        else:
            return []

    if status:
        query = query.filter(model_cls.status == status)

    return query.order_by(model_cls.created_at.desc()).offset(skip).limit(limit).all()


# ──────────────────────────────────────────────
# 查询所有类别的成果（学生用 - 我的提交记录）
# ──────────────────────────────────────────────
@router.get("/my-all", summary="查询我的所有成果")
async def list_my_all_achievements(
    student_id: str = Query(...),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        return []

    results = []
    for cat_name, model_cls in CATEGORY_MODELS.items():
        items = db.query(model_cls).filter(model_cls.student_db_id == student.id).all()
        for item in items:
            display_name = _get_display_name(item, cat_name)
            results.append({
                "id": item.id,
                "category": cat_name,
                "display_name": display_name,
                "status": item.status,
                "certificate_image": item.certificate_image,
                "created_at": item.created_at.isoformat() if item.created_at else "",
            })

    results.sort(key=lambda x: x["created_at"], reverse=True)
    return results


def _get_display_name(item, category: str) -> str:
    if category == "科研项目":
        return item.project_name
    elif category == "专利软著":
        return item.name
    elif category == "学术论文":
        return item.paper_name
    elif category == "学科竞赛":
        return item.competition_name
    return ""


# ──────────────────────────────────────────────
# 更新状态（辅导员审核）
# ──────────────────────────────────────────────
@router.patch("/{category}/{item_id}/status", response_model=MessageResponse, summary="更新成果状态")
async def update_status(
    category: str,
    item_id: int,
    status: str = Query(...),
    db: Session = Depends(get_db),
):
    if category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"无效类别")
    if status not in ("confirmed", "rejected", "pending"):
        raise HTTPException(status_code=400, detail="无效状态")

    model_cls = CATEGORY_MODELS[category]
    record = db.query(model_cls).filter(model_cls.id == item_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="成果记录不存在")

    record.status = status
    db.commit()
    return MessageResponse(message=f"状态已更新为 {status}")
