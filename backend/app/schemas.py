"""
Pydantic 数据模型（请求 / 响应 Schema）
用于 API 数据校验与序列化
"""

from datetime import datetime
from typing import List, Optional

import re

from pydantic import BaseModel, Field, field_validator


# ──────────────────────────────────────────────
# 认证 Schema
# ──────────────────────────────────────────────
class RegisterRequest(BaseModel):
    """学生注册"""
    username: str = Field(..., description="学号（11位数字）")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    name: str = Field(..., description="姓名（中文）")
    class_name: str = Field(..., description="班级（如 2025级英语2班）")
    major: str = Field(default="", description="学院（如 外国语言与文化学院）")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
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


class LoginRequest(BaseModel):
    """登录（学生 & 辅导员通用）"""
    username: str = Field(..., description="学号或辅导员用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """登录成功响应"""
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    username: str
    name: str
    role: str
    class_name: str
    major: str

    model_config = {"from_attributes": True}


# 解决前向引用
TokenResponse.model_rebuild()


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
# LLM 识别结果 Schema（按类别区分）
# ──────────────────────────────────────────────
class ResearchProjectExtract(BaseModel):
    project_number: str = Field(default="", description="立项编号")
    project_level: str = Field(default="", description="项目层级")
    project_name: str = Field(default="", description="参与科研项目名称")
    student_rank: str = Field(default="", description="学生排名")
    project_year: str = Field(default="", description="立项年度")
    project_source: str = Field(default="", description="项目来源")
    project_leader: str = Field(default="", description="项目负责人")
    leader_id: str = Field(default="", description="工号")
    counselor_name: str = Field(default="", description="辅导员姓名")


class PatentExtract(BaseModel):
    name: str = Field(default="", description="名称")
    patent_type: str = Field(default="", description="类别")
    authorization_number: str = Field(default="", description="授权号")
    approval_date: str = Field(default="", description="获批时间")
    inventor_rank: str = Field(default="", description="发明人排名")
    counselor_name: str = Field(default="", description="辅导员姓名")


class PaperExtract(BaseModel):
    paper_name: str = Field(default="", description="论文名称")
    journal_name: str = Field(default="", description="发表期刊名称")
    author_rank: str = Field(default="", description="作者排名")
    publish_date: str = Field(default="", description="发表时间")
    indexing: str = Field(default="", description="收录情况")
    paper_link: str = Field(default="", description="论文链接")
    counselor_name: str = Field(default="", description="辅导员姓名")


class CompetitionExtract(BaseModel):
    competition_name: str = Field(default="", description="赛事名称")
    track: str = Field(default="", description="赛道")
    organizer: str = Field(default="", description="赛事主办方")
    project_name: str = Field(default="", description="项目名称")
    award_name: str = Field(default="", description="奖项名称")
    team_leader: str = Field(default="", description="项目负责人")
    phone: str = Field(default="", description="联系电话")
    advisor: str = Field(default="", description="指导老师")
    team_members: str = Field(default="", description="学生成员")
    award_date: str = Field(default="", description="获奖时间")
    remark: str = Field(default="", description="备注")


# ──────────────────────────────────────────────
# 成果 Create Schema（4 类）
# ──────────────────────────────────────────────
class ResearchProjectCreate(BaseModel):
    student_db_id: int = Field(..., description="学生数据库ID")
    project_number: str = Field(default="")
    project_level: str = Field(default="")
    project_name: str = Field(..., min_length=1, max_length=200)
    student_rank: str = Field(default="")
    project_year: str = Field(default="")
    project_source: str = Field(default="")
    project_leader: str = Field(default="")
    leader_id: str = Field(default="")
    counselor_name: str = Field(default="")
    certificate_image: str = Field(default="")


class PatentCreate(BaseModel):
    student_db_id: int = Field(..., description="学生数据库ID")
    name: str = Field(..., min_length=1, max_length=200)
    patent_type: str = Field(default="")
    authorization_number: str = Field(default="")
    approval_date: str = Field(default="")
    inventor_rank: str = Field(default="")
    counselor_name: str = Field(default="")
    certificate_image: str = Field(default="")


class PaperCreate(BaseModel):
    student_db_id: int = Field(..., description="学生数据库ID")
    paper_name: str = Field(..., min_length=1, max_length=300)
    journal_name: str = Field(default="")
    author_rank: str = Field(default="")
    publish_date: str = Field(default="")
    indexing: str = Field(default="")
    paper_link: str = Field(default="")
    counselor_name: str = Field(default="")
    certificate_image: str = Field(default="")


class CompetitionCreate(BaseModel):
    student_db_id: int = Field(..., description="学生数据库ID")
    competition_name: str = Field(..., min_length=1, max_length=200)
    track: str = Field(default="")
    organizer: str = Field(default="")
    project_name: str = Field(default="")
    award_name: str = Field(default="")
    team_leader: str = Field(default="")
    phone: str = Field(default="")
    advisor: str = Field(default="")
    team_members: str = Field(default="")
    award_date: str = Field(default="")
    remark: str = Field(default="")
    certificate_image: str = Field(default="")


# ──────────────────────────────────────────────
# 成果 Out Schema（4 类）
# ──────────────────────────────────────────────
class ResearchProjectOut(BaseModel):
    id: int
    student_db_id: int
    project_number: str
    project_level: str
    project_name: str
    student_rank: str
    project_year: str
    project_source: str
    project_leader: str
    leader_id: str
    counselor_name: str
    certificate_image: str
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ResearchProjectWithStudent(ResearchProjectOut):
    student: StudentOut


class PatentOut(BaseModel):
    id: int
    student_db_id: int
    name: str
    patent_type: str
    authorization_number: str
    approval_date: str
    inventor_rank: str
    counselor_name: str
    certificate_image: str
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class PatentWithStudent(PatentOut):
    student: StudentOut


class PaperOut(BaseModel):
    id: int
    student_db_id: int
    paper_name: str
    journal_name: str
    author_rank: str
    publish_date: str
    indexing: str
    paper_link: str
    counselor_name: str
    certificate_image: str
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class PaperWithStudent(PaperOut):
    student: StudentOut


class CompetitionOut(BaseModel):
    id: int
    student_db_id: int
    competition_name: str
    track: str
    organizer: str
    project_name: str
    award_name: str
    team_leader: str
    phone: str
    advisor: str
    team_members: str
    award_date: str
    certificate_image: str
    remark: str
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class CompetitionWithStudent(CompetitionOut):
    student: StudentOut


# ──────────────────────────────────────────────
# 通用响应
# ──────────────────────────────────────────────
class UploadResponse(BaseModel):
    image_path: str = Field(..., description="上传后的图片路径")
    category: str = Field(..., description="成果类别")
    extracted: dict = Field(..., description="LLM 提取的结构化数据")
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
    replies: list[FeedbackReplyOut] = Field(default_factory=list)


# ──────────────────────────────────────────────
# 考勤模块 Schema
# ──────────────────────────────────────────────
class ClassRosterOut(BaseModel):
    id: int
    student_id: str
    name: str
    gender: str
    class_name: str
    major: str
    phone: str
    counselor: str

    model_config = {"from_attributes": True}


class CourseScheduleCreate(BaseModel):
    class_name: str = Field(..., description="年级专业班级")
    week_number: int = Field(..., description="教学周数")
    day_of_week: str = Field(..., description="星期几")
    period: str = Field(..., description="节次")
    course_name: str = Field(..., description="课程名称")
    teacher: str = Field(default="", description="授课教师")
    classroom: str = Field(default="", description="教室")
    date_str: str = Field(default="", description="日期")


class CourseScheduleOut(BaseModel):
    id: int
    class_name: str
    week_number: int
    day_of_week: str
    period: str
    course_name: str
    teacher: str
    classroom: str
    date_str: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AttendanceRecordCreate(BaseModel):
    schedule_id: Optional[int] = Field(default=None, description="关联课程ID")
    class_name: str = Field(..., description="年级专业班级")
    date_str: str = Field(..., description="日期")
    day_of_week: str = Field(..., description="星期几")
    period: str = Field(..., description="节次")
    course_name: str = Field(..., description="课程名称")
    teacher: str = Field(default="", description="授课教师")
    classroom: str = Field(default="", description="教室")
    class_size: int = Field(default=0, description="班级人数")
    actual_count: int = Field(default=0, description="实到人数")
    sick_leave_count: int = Field(default=0, description="病/公假人数")
    personal_leave_count: int = Field(default=0, description="事假人数")
    late_count: int = Field(default=0, description="迟到人数")
    early_leave_count: int = Field(default=0, description="早退人数")
    absent_count: int = Field(default=0, description="旷课人数")
    leave_details: str = Field(default="", description="请假情况说明")
    checker: str = Field(default="", description="检查人")
    week_number: int = Field(default=0, description="教学周数")
    classroom_photos: List[str] = Field(default=[], description="教室照片路径列表（必须2张）")
    leave_slips: List["LeaveSlipItem"] = Field(default=[], description="假条图片列表")


class LeaveSlipItem(BaseModel):
    student_id: str = Field(..., description="学号")
    student_name: str = Field(default="", description="学生姓名")
    reason: str = Field(default="", description="原因")
    image_path: str = Field(..., description="假条图片路径")


class LeaveSlipOut(BaseModel):
    id: int
    student_id: str
    student_name: str
    reason: str
    image_path: str

    model_config = {"from_attributes": True}


class AttendanceRecordOut(BaseModel):
    id: int
    schedule_id: Optional[int]
    class_name: str
    date_str: str
    day_of_week: str
    period: str
    course_name: str
    teacher: str
    classroom: str
    class_size: int
    actual_count: int
    sick_leave_count: int
    personal_leave_count: int
    late_count: int
    early_leave_count: int
    absent_count: int
    not_arrived_count: int
    attendance_rate: str
    attendance_rate_with_leave: str
    hygiene: str
    discipline: str
    discipline_count: int
    violation_rate: str
    leave_details: str
    classroom_photos: str
    checker: str
    week_number: int
    created_at: datetime
    leave_slips: List[LeaveSlipOut] = Field(default=[], description="请假条图片列表")

    model_config = {"from_attributes": True}


class CheckInSessionCreate(BaseModel):
    class_name: str = Field(..., description="年级专业班级")
    course_name: str = Field(default="", description="课程名称")
    expire_minutes: int = Field(default=5, ge=1, le=30, description="过期时间（分钟）")
    schedule_id: Optional[int] = Field(default=None, description="关联的课程表ID")


class CheckInSessionOut(BaseModel):
    id: int
    code: str
    class_name: str
    course_name: str
    expire_minutes: int
    is_active: bool
    created_at: datetime
    log_count: int = Field(default=0, description="已签到人数")

    model_config = {"from_attributes": True}


class CheckInLogOut(BaseModel):
    id: int
    session_id: int
    user_id: int
    student_name: str
    student_number: str
    status: str
    checked_at: datetime

    model_config = {"from_attributes": True}
