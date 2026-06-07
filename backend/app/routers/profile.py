"""
成长画像路由
学生端：查看个人成长画像
辅导员端：查看全班成长画像和总体情况
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import (
    User, ClassRoster, Student,
    ResearchProject, Patent, Paper, Competition
)
from ..services.auth_service import get_current_user

router = APIRouter(prefix="/api/v1/profile", tags=["成长画像"])


@router.get("/student/me")
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """学生查看自己的成长画像"""
    if current_user.role not in ["student", "monitor"]:
        raise HTTPException(status_code=403, detail="仅学生可访问")

    # 获取花名册信息
    roster = db.query(ClassRoster).filter(
        ClassRoster.student_id == current_user.username
    ).first()

    # 获取学生成果记录
    student = db.query(Student).filter(
        Student.student_id == current_user.username
    ).first()

    # 统计成果数量
    achievements = {
        "research_projects": 0,
        "patents": 0,
        "papers": 0,
        "competitions": 0,
        "total": 0
    }

    if student:
        achievements["research_projects"] = db.query(ResearchProject).filter(
            ResearchProject.student_db_id == student.id,
            ResearchProject.status == "confirmed"
        ).count()

        achievements["patents"] = db.query(Patent).filter(
            Patent.student_db_id == student.id,
            Patent.status == "confirmed"
        ).count()

        achievements["papers"] = db.query(Paper).filter(
            Paper.student_db_id == student.id,
            Paper.status == "confirmed"
        ).count()

        achievements["competitions"] = db.query(Competition).filter(
            Competition.student_db_id == student.id,
            Competition.status == "confirmed"
        ).count()

        achievements["total"] = sum([
            achievements["research_projects"],
            achievements["patents"],
            achievements["papers"],
            achievements["competitions"]
        ])

    return {
        "basic_info": {
            "student_id": current_user.username,
            "name": current_user.name,
            "class_name": roster.class_name if roster else current_user.class_name,
            "major": roster.major if roster else current_user.major,
            "gender": roster.gender if roster else "",
            "ethnicity": roster.ethnicity if roster else "",
            "political_status": roster.political_status if roster else "",
            "phone": roster.phone if roster else "",
            "hometown": roster.hometown if roster else "",
            "home_address": roster.home_address if roster else "",
            "parent_name": roster.parent_name if roster else "",
            "parent_phone": roster.parent_phone if roster else "",
            "dorm_nickname": roster.dorm_nickname if roster else "",
            "dorm_address": roster.dorm_address if roster else "",
            "education_level": roster.education_level if roster else "",
            "grade": roster.grade if roster else "",
            "specialty": roster.specialty if roster else "",
            "counselor": roster.counselor if roster else ""
        },
        "achievements": achievements
    }


@router.get("/counselor/class-overview")
def get_class_overview(
    class_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """辅导员查看全班成长画像总览"""
    if current_user.role != "counselor":
        raise HTTPException(status_code=403, detail="仅辅导员可访问")

    # 获取班级列表
    classes = db.query(ClassRoster.class_name).distinct().all()
    class_list = [c[0] for c in classes]

    # 如果没有指定班级，默认第一个班级
    if not class_name and class_list:
        class_name = class_list[0]

    # 获取该班级所有学生
    students = db.query(ClassRoster).filter(
        ClassRoster.class_name == class_name
    ).all()

    # 统计班级总体数据
    total_students = len(students)
    students_with_achievements = 0
    total_achievements = {
        "research_projects": 0,
        "patents": 0,
        "papers": 0,
        "competitions": 0
    }

    # 学生详细画像列表
    student_profiles = []

    for roster in students:
        student = db.query(Student).filter(
            Student.student_id == roster.student_id
        ).first()

        achievements = {
            "research_projects": 0,
            "patents": 0,
            "papers": 0,
            "competitions": 0,
            "total": 0
        }

        if student:
            achievements["research_projects"] = db.query(ResearchProject).filter(
                ResearchProject.student_db_id == student.id,
                ResearchProject.status == "confirmed"
            ).count()

            achievements["patents"] = db.query(Patent).filter(
                Patent.student_db_id == student.id,
                Patent.status == "confirmed"
            ).count()

            achievements["papers"] = db.query(Paper).filter(
                Paper.student_db_id == student.id,
                Paper.status == "confirmed"
            ).count()

            achievements["competitions"] = db.query(Competition).filter(
                Competition.student_db_id == student.id,
                Competition.status == "confirmed"
            ).count()

            achievements["total"] = sum([
                achievements["research_projects"],
                achievements["patents"],
                achievements["papers"],
                achievements["competitions"]
            ])

            # 累加到班级总数
            total_achievements["research_projects"] += achievements["research_projects"]
            total_achievements["patents"] += achievements["patents"]
            total_achievements["papers"] += achievements["papers"]
            total_achievements["competitions"] += achievements["competitions"]

            if achievements["total"] > 0:
                students_with_achievements += 1

        student_profiles.append({
            "student_id": roster.student_id,
            "name": roster.name,
            "gender": roster.gender,
            "ethnicity": roster.ethnicity,
            "political_status": roster.political_status,
            "phone": roster.phone,
            "hometown": roster.hometown,
            "parent_name": roster.parent_name,
            "parent_phone": roster.parent_phone,
            "dorm_nickname": roster.dorm_nickname,
            "achievements": achievements
        })

    # 计算参与率
    participation_rate = round(students_with_achievements / total_students * 100, 1) if total_students > 0 else 0

    return {
        "class_list": class_list,
        "current_class": class_name,
        "summary": {
            "total_students": total_students,
            "students_with_achievements": students_with_achievements,
            "participation_rate": participation_rate,
            "total_achievements": total_achievements,
            "total_count": sum(total_achievements.values())
        },
        "students": student_profiles
    }
