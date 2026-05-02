"""
数据导出路由
辅导员可以按类别一键导出 Excel
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Competition, Paper, Patent, ResearchProject, Student
from ..services.excel_service import generate_category_excel

router = APIRouter()

CATEGORY_MODELS = {
    "科研项目": ResearchProject,
    "专利软著": Patent,
    "学术论文": Paper,
    "学科竞赛": Competition,
}

CATEGORY_FILENAMES = {
    "科研项目": "学生科研项目情况统计表.xlsx",
    "专利软著": "学生专利软著授权情况统计表.xlsx",
    "学术论文": "学生学术论文发表情况统计表.xlsx",
    "学科竞赛": "学科竞赛获奖情况统计表.xlsx",
}


@router.get("/achievements/excel", summary="导出成果 Excel")
async def export_achievements_excel(
    category: str = Query(..., description="成果类别"),
    status: Optional[str] = "confirmed",
    db: Session = Depends(get_db),
):
    if category not in CATEGORY_MODELS:
        raise HTTPException(status_code=400, detail=f"无效类别: {category}")

    model_cls = CATEGORY_MODELS[category]
    query = (
        db.query(model_cls, Student)
        .join(Student, model_cls.student_db_id == Student.id)
    )

    if status:
        query = query.filter(model_cls.status == status)

    records = query.order_by(model_cls.created_at.desc()).all()

    file_path = generate_category_excel(category, records)

    return FileResponse(
        path=file_path,
        filename=CATEGORY_FILENAMES[category],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
