"""
Pydantic 数据模型（请求 / 响应 Schema）
用于 API 数据校验与序列化
"""

from datetime import datetime

import re

from pydantic import BaseModel, Field, field_validator


# ──────────────────────────────────────────────
# 学生 Schema
# ──────────────────────────────────────────────
class StudentCreate(BaseModel):
    student_id: str = Field(..., description="学号（11位数字）")
    name: str = Field(..., description="姓名（中文）")
    class_name: str = Field(..., description="班级（如 2025级英语2班）")
    major: str = Field(default="", description="学院（如 外国语言与文化学院）")
    phone: str = Field(default="", max_length=20, description="联系电话")

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, v):
        if not re.match(r"^\d{11}$", v):
            raise ValueError("学号必须为11位数字")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not re.match(r"^[\u4e00-\u9fa5\u00b7]{2,20}$", v):
            raise ValueError("姓名只能输入中文（2-20个字）")
        return v

    @field_validator("class_name")
    @classmethod
    def validate_class_name(cls, v):
        if not re.match(r"^\d{4}级.+\d+班$", v):
            raise ValueError("班级格式：年级+专业+班号，如 2025级英语2班")
        return v

    @field_validator("major")
    @classmethod
    def validate_major(cls, v):
        if v and not re.match(r"^[\u4e00-\u9fa5（）()]{4,30}$", v):
            raise ValueError("请输入完整学院名称，如 外国语言与文化学院")
        return v


class StudentOut(BaseModel):
    id: int
    student_id: str
    name: str
    class_name: str
    major: str
    phone: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# LLM 识别结果 Schema
# ──────────────────────────────────────────────
class LLMExtractResult(BaseModel):
    """LLM 从证书图片中提取的结构化数据"""
    competition_name: str = Field(default="", description="比赛/项目名称")
    winner_name: str = Field(default="", description="获奖人姓名")
    award_level: str = Field(default="", description="获奖等级")
    award_date: str = Field(default="", description="获奖日期")


# ──────────────────────────────────────────────
# 成果 Schema
# ──────────────────────────────────────────────
class AchievementCreate(BaseModel):
    """学生确认后提交的成果数据"""
    student_db_id: int = Field(..., description="学生数据库ID")
    competition_name: str = Field(..., min_length=1, max_length=200)
    winner_name: str = Field(..., min_length=1, max_length=100)
    award_level: str = Field(..., min_length=1, max_length=50)
    award_date: str = Field(default="", max_length=30)
    category: str = Field(default="其他")
    certificate_image: str = Field(..., description="证书图片路径")


class AchievementOut(BaseModel):
    id: int
    student_db_id: int
    competition_name: str
    winner_name: str
    award_level: str
    award_date: str
    category: str
    certificate_image: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AchievementWithStudent(AchievementOut):
    """包含学生信息的成果（用于导出）"""
    student: StudentOut


# ──────────────────────────────────────────────
# 通用响应
# ──────────────────────────────────────────────
class UploadResponse(BaseModel):
    """上传 + LLM 识别后的响应"""
    image_path: str = Field(..., description="上传后的图片路径")
    extracted: LLMExtractResult = Field(..., description="LLM 提取的结构化数据")
    raw_response: str = Field(default="", description="LLM 原始返回")


class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ──────────────────────────────────────────────
# 树洞（匿名反馈）Schema
# ──────────────────────────────────────────────
class FeedbackCreate(BaseModel):
    """学生提交匿名反馈"""
    content: str = Field(..., min_length=1, max_length=2000, description="反馈内容")
    category: str = Field(default="其他", description="分类标签")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        allowed = {"寝室矛盾", "学业压力", "教学建议", "心理困惑", "其他"}
        if v not in allowed:
            raise ValueError(f"分类必须是 {allowed} 之一")
        return v


class FeedbackReplyCreate(BaseModel):
    """回复反馈"""
    content: str = Field(..., min_length=1, max_length=1000, description="回复内容")
    is_counselor: bool = Field(default=False, description="是否为辅导员回复")


class FeedbackReplyOut(BaseModel):
    id: int
    feedback_id: int
    content: str
    is_counselor: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackOut(BaseModel):
    id: int
    anonymous_id: str
    content: str
    category: str
    emotion_score: float
    emotion_label: str
    is_urgent: bool
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FeedbackDetail(FeedbackOut):
    """包含对话记录的反馈详情"""
    replies: list = Field(default_factory=list)
