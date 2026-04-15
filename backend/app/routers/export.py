"""
数据导出路由
辅导员可以一键导出 Excel
"""

from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Achievement, Student
from ..services.excel_service import generate_achievement_excel

router = APIRouter()


@router.get("/achievements/excel", summary="导出成果 Excel")
async def export_achievements_excel(
    status: Optional[str] = "confirmed",
    db: Session = Depends(get_db),
):
    """
    步骤4：辅导员一键导出所有已确认的成果记录为 Excel 文件
    """
    query = (
        db.query(Achievement, Student)
        .join(Student, Achievement.student_db_id == Student.id)
    )

    if status:
        query = query.filter(Achievement.status == status)

    records = query.order_by(Achievement.created_at.desc()).all()

    # 组装导出数据
    export_data = []
    for achievement, student in records:
        export_data.append({
            "学号": student.student_id,
            "上报人": student.name,
            "班级": student.class_name,
            "学院": student.major,
            "比赛/项目名称": achievement.competition_name,
            "获奖人（AI识别）": achievement.winner_name,
            "获奖等级": achievement.award_level,
            "获奖日期": achievement.award_date,
            "成果分类": achievement.category,
            "状态": achievement.status,
            "提交时间": achievement.created_at.strftime("%Y-%m-%d %H:%M"),
            "_image_path": achievement.certificate_image,  # 供 Excel 嵌入图片
        })

    file_path = generate_achievement_excel(export_data)

    return FileResponse(
        path=file_path,
        filename="科研与比赛成果汇总.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
