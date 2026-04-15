"""
数据库模型定义
使用 SQLAlchemy ORM 映射数据库表
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


# ──────────────────────────────────────────────
# 学生表
# ──────────────────────────────────────────────
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(20), unique=True, nullable=False, index=True, comment="学号")
    name = Column(String(50), nullable=False, comment="姓名")
    class_name = Column(String(50), nullable=False, comment="班级")
    major = Column(String(100), default="", comment="专业")
    phone = Column(String(20), default="", comment="联系电话")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关联：一个学生可以有多条成果记录
    achievements = relationship("Achievement", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(student_id={self.student_id}, name={self.name})>"


# ──────────────────────────────────────────────
# 科研/比赛成果表
# ──────────────────────────────────────────────
class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_db_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="关联学生ID")

    # ---- LLM 提取字段 ----
    competition_name = Column(String(200), nullable=False, comment="比赛/项目名称")
    winner_name = Column(String(100), nullable=False, comment="获奖人姓名")
    award_level = Column(String(50), nullable=False, comment="获奖等级（如：一等奖、金奖）")
    award_date = Column(String(30), default="", comment="获奖日期（原始文本）")

    # ---- 附加信息 ----
    category = Column(
        Enum("科研", "学科竞赛", "创新创业", "文体活动", "其他", name="achievement_category"),
        default="其他",
        comment="成果分类",
    )
    certificate_image = Column(String(500), nullable=False, comment="证书图片路径")
    raw_llm_response = Column(Text, default="", comment="LLM 原始返回 JSON")

    # ---- 审核状态 ----
    status = Column(
        Enum("pending", "confirmed", "rejected", name="achievement_status"),
        default="pending",
        index=True,
        comment="状态：待确认 / 已确认 / 已驳回",
    )

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联
    student = relationship("Student", back_populates="achievements")

    def __repr__(self):
        return f"<Achievement(competition={self.competition_name}, winner={self.winner_name}, level={self.award_level})>"


# ──────────────────────────────────────────────
# 匿名反馈（树洞）表
# ──────────────────────────────────────────────
class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    anonymous_id = Column(String(20), unique=True, nullable=False, index=True, comment="匿名ID（如 树洞#A3F8K2）")
    content = Column(Text, nullable=False, comment="反馈内容")

    # ---- 分类标签 ----
    category = Column(
        Enum("寝室矛盾", "学业压力", "教学建议", "心理困惑", "其他", name="feedback_category"),
        default="其他",
        index=True,
        comment="反馈分类",
    )

    # ---- AI 情绪分析 ----
    emotion_score = Column(Float, default=5.0, comment="情绪评分 1-10（1=极度消极）")
    emotion_label = Column(String(20), default="", comment="情绪标签（如：焦虑、平和）")
    is_urgent = Column(Boolean, default=False, index=True, comment="是否紧急预警（评分≤3自动标记）")

    # ---- 状态 ----
    status = Column(
        Enum("pending", "replied", "closed", name="feedback_status"),
        default="pending",
        index=True,
        comment="状态：待回复 / 已回复 / 已关闭",
    )

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联：一条反馈可以有多条回复（双向对话）
    replies = relationship("FeedbackReply", back_populates="feedback", cascade="all, delete-orphan", order_by="FeedbackReply.created_at")

    def __repr__(self):
        return f"<Feedback(id={self.anonymous_id}, category={self.category}, score={self.emotion_score})>"


# ──────────────────────────────────────────────
# 树洞回复表（双向匿名对话）
# ──────────────────────────────────────────────
class FeedbackReply(Base):
    __tablename__ = "feedback_replies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feedback_id = Column(Integer, ForeignKey("feedbacks.id"), nullable=False, comment="关联反馈ID")
    content = Column(Text, nullable=False, comment="回复内容")
    is_counselor = Column(Boolean, default=False, comment="是否为辅导员回复")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关联
    feedback = relationship("Feedback", back_populates="replies")

    def __repr__(self):
        role = "辅导员" if self.is_counselor else "学生"
        return f"<FeedbackReply(role={role}, feedback_id={self.feedback_id})>"
