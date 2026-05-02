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
# 用户表（学生 + 辅导员统一）
# ──────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名（学生为学号）")
    password_hash = Column(String(200), nullable=False, comment="加密后的密码")
    name = Column(String(50), nullable=False, comment="真实姓名")
    role = Column(
        Enum("student", "counselor", "monitor", name="user_role"),
        nullable=False,
        default="student",
        comment="角色：student / counselor / monitor（纪律委员）",
    )
    # 学生专属字段
    class_name = Column(String(50), default="", comment="班级")
    major = Column(String(100), default="", comment="学院")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"


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

    # 关联
    research_projects = relationship("ResearchProject", back_populates="student", cascade="all, delete-orphan")
    patents = relationship("Patent", back_populates="student", cascade="all, delete-orphan")
    papers = relationship("Paper", back_populates="student", cascade="all, delete-orphan")
    competitions = relationship("Competition", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(student_id={self.student_id}, name={self.name})>"


# ──────────────────────────────────────────────
# 科研项目表
# ──────────────────────────────────────────────
class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_db_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    project_number = Column(String(50), default="", comment="立项编号")
    project_level = Column(String(30), default="", comment="项目层级（国家���/省级/市厅级/校级）")
    project_name = Column(String(200), nullable=False, comment="参与科研项目名称")
    student_rank = Column(String(20), default="", comment="学生排名")
    project_year = Column(String(10), default="", comment="立项年度")
    project_source = Column(String(100), default="", comment="项目来源")
    project_leader = Column(String(50), default="", comment="项目负责人")
    leader_id = Column(String(30), default="", comment="工号")
    counselor_name = Column(String(50), default="", comment="辅导员姓名")

    certificate_image = Column(String(500), default="", comment="证书图片路径")
    status = Column(
        Enum("pending", "confirmed", "rejected", name="rp_status"),
        default="pending", index=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="research_projects")


# ──────────────────────────────────────────────
# 专利软著表
# ──────────────────────────────────────────────
class Patent(Base):
    __tablename__ = "patents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_db_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    name = Column(String(200), nullable=False, comment="名称")
    patent_type = Column(String(50), default="", comment="类别（实用新型专利/软著等）")
    authorization_number = Column(String(50), default="", comment="授权号")
    approval_date = Column(String(30), default="", comment="获批时间")
    inventor_rank = Column(String(20), default="", comment="发明人排名")
    counselor_name = Column(String(50), default="", comment="辅导员姓名")

    certificate_image = Column(String(500), default="", comment="证书图片路径")
    status = Column(
        Enum("pending", "confirmed", "rejected", name="patent_status"),
        default="pending", index=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="patents")


# ──────────────────────────────────────────────
# 学术论文表
# ──────────────────────────────────────────────
class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_db_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    paper_name = Column(String(300), nullable=False, comment="论文名称")
    journal_name = Column(String(200), default="", comment="发表期刊名称")
    author_rank = Column(String(20), default="", comment="作者排名")
    publish_date = Column(String(30), default="", comment="发表时间")
    indexing = Column(String(50), default="", comment="收录情况（CSSCI/SCI/普刊等）")
    paper_link = Column(String(500), default="", comment="论文链接")
    counselor_name = Column(String(50), default="", comment="辅导员姓名")

    certificate_image = Column(String(500), default="", comment="证书图片路径")
    status = Column(
        Enum("pending", "confirmed", "rejected", name="paper_status"),
        default="pending", index=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="papers")


# ──────────────────────────────────────────────
# 学科竞赛表
# ──────────────────────────────────────────────
class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_db_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    competition_name = Column(String(200), nullable=False, comment="赛事名称")
    track = Column(String(100), default="", comment="赛道")
    organizer = Column(String(200), default="", comment="赛事主办方")
    project_name = Column(String(200), default="", comment="项目名称")
    award_name = Column(String(100), default="", comment="奖项名称")
    team_leader = Column(String(50), default="", comment="项目负责人")
    phone = Column(String(20), default="", comment="联系电话")
    advisor = Column(String(200), default="", comment="指导老师（全部）")
    team_members = Column(String(500), default="", comment="学生成员（全部）")
    award_date = Column(String(30), default="", comment="获奖时间")
    certificate_image = Column(String(500), default="", comment="获奖证书图片路径")
    remark = Column(String(500), default="", comment="备注")

    status = Column(
        Enum("pending", "confirmed", "rejected", name="comp_status"),
        default="pending", index=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="competitions")


# ──────────────────────────────────────────────
# 匿名反馈（树洞）表
# ──────────────────────────────────────────────
class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    anonymous_id = Column(String(50), unique=True, nullable=False, index=True, comment="匿名昵称（如 树洞·冒泡的小水獭07）")
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


# ──────────────────────────────────────────────
# 班级花名册表
# ──────────────────────────────────────────────
class ClassRoster(Base):
    __tablename__ = "class_rosters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(20), nullable=False, index=True, comment="学号")
    name = Column(String(50), nullable=False, comment="姓名")
    gender = Column(String(10), default="", comment="性别")
    class_name = Column(String(50), nullable=False, index=True, comment="年级专业班级")
    major = Column(String(100), default="", comment="所属院系")
    phone = Column(String(20), default="", comment="联系电话")
    counselor = Column(String(50), default="", comment="辅导员")
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ClassRoster(student_id={self.student_id}, name={self.name})>"


# ──────────────────────────────────────────────
# 课程表（每周课程信息）
# ──────────────────────────────────────────────
class CourseSchedule(Base):
    __tablename__ = "course_schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String(50), nullable=False, index=True, comment="年级专业班级")
    week_number = Column(Integer, nullable=False, comment="教学周数")
    day_of_week = Column(String(10), nullable=False, comment="星期几（周一~周日）")
    period = Column(String(20), nullable=False, comment="节次（如 1-2, 3-4）")
    course_name = Column(String(100), nullable=False, comment="课程名称")
    teacher = Column(String(50), default="", comment="授课教师")
    classroom = Column(String(50), default="", comment="教室")
    date_str = Column(String(20), default="", comment="日期（如 3.2）")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建者ID")
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CourseSchedule({self.class_name} {self.day_of_week} {self.period} {self.course_name})>"


# ──────────────────────────────────────────────
# 考勤记录表（一键考勤）
# ──────────────────────────────────────────────
class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("course_schedules.id"), nullable=True, comment="关联课程")
    class_name = Column(String(50), nullable=False, index=True, comment="年级专业班级")
    date_str = Column(String(20), nullable=False, comment="日期（如 3.2）")
    day_of_week = Column(String(10), nullable=False, comment="星期几")
    period = Column(String(20), nullable=False, comment="节次")
    course_name = Column(String(100), nullable=False, comment="课程名称")
    teacher = Column(String(50), default="", comment="授课教师")
    classroom = Column(String(50), default="", comment="教室")

    class_size = Column(Integer, default=0, comment="班级人数")
    actual_count = Column(Integer, default=0, comment="实到人数")
    sick_leave_count = Column(Integer, default=0, comment="病/公假人数")
    personal_leave_count = Column(Integer, default=0, comment="事假人数")
    late_count = Column(Integer, default=0, comment="迟到人数")
    early_leave_count = Column(Integer, default=0, comment="早退人数")
    absent_count = Column(Integer, default=0, comment="旷课人数")
    not_arrived_count = Column(Integer, default=0, comment="未到人数")
    attendance_rate = Column(String(10), default="", comment="到课率（实到/班级人数）")
    attendance_rate_with_leave = Column(String(10), default="", comment="到课率（含请假）")

    hygiene = Column(String(10), default="良好", comment="教室卫生情况")
    discipline = Column(String(10), default="良好", comment="课堂纪律情况")
    discipline_count = Column(Integer, default=0, comment="违纪人数")
    violation_rate = Column(String(10), default="0%", comment="违纪率")

    leave_details = Column(Text, default="", comment="请假、违纪情况说明")
    checker = Column(String(50), default="", comment="检查人")
    week_number = Column(Integer, default=0, comment="教学周数")

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建者ID")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AttendanceRecord({self.class_name} {self.date_str} {self.course_name})>"


# ──────────────────────────────────────────────
# 签到抽查会话表（二维码签到）
# ──────────────────────────────────────────────
class CheckInSession(Base):
    __tablename__ = "checkin_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(32), unique=True, nullable=False, index=True, comment="签到码（用于生成二维码）")
    class_name = Column(String(50), nullable=False, comment="年级专业班级")
    course_name = Column(String(100), default="", comment="课程名称")
    expire_minutes = Column(Integer, default=5, comment="过期时间（分钟）")
    is_active = Column(Boolean, default=True, index=True, comment="是否有效")
    schedule_id = Column(Integer, ForeignKey("course_schedules.id"), nullable=True, comment="关联的课程表ID")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建者（纪律委员）")
    created_at = Column(DateTime, default=datetime.utcnow)

    logs = relationship("CheckInLog", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CheckInSession(code={self.code}, class={self.class_name})>"


# ────────────���─────────────────────────────────
# 签到日志表
# ──────────────────────────────────────────────
class CheckInLog(Base):
    __tablename__ = "checkin_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("checkin_sessions.id"), nullable=False, comment="关联签到会话")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="签到用户")
    student_name = Column(String(50), default="", comment="学生姓名")
    student_number = Column(String(20), default="", comment="学号")
    status = Column(String(20), default="正常", comment="签到状态：正常/病假/公假/事假/迟到/早退")
    checked_at = Column(DateTime, default=datetime.utcnow, comment="签到时间")

    session = relationship("CheckInSession", back_populates="logs")

    def __repr__(self):
        return f"<CheckInLog(session={self.session_id}, user={self.user_id})>"
