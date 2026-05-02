"""
认证路由：注册 / 登录
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Student
from ..schemas import RegisterRequest, LoginRequest, TokenResponse, UserOut
from ..services.auth_service import (
    hash_password,
    verify_password,
    create_token,
    get_current_user,
    require_counselor,
)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, summary="学生注册")
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """学生用学号注册账号"""
    # 检查学号是否已注册
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="该学号已注册，请直接登录")

    # 创建用户
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        name=data.name,
        role="student",
        class_name=data.class_name,
        major=data.major,
    )
    db.add(user)
    db.flush()  # 拿到 user.id

    # 同步创建 Student 记录（兼容现有成果模块）
    existing_student = db.query(Student).filter(Student.student_id == data.username).first()
    if not existing_student:
        student = Student(
            student_id=data.username,
            name=data.name,
            class_name=data.class_name,
            major=data.major,
        )
        db.add(student)

    db.commit()
    db.refresh(user)

    token = create_token(user.id, user.username, user.role)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenResponse, summary="登录（学生/辅导员通用）")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """统一登录入口"""
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_token(user.id, user.username, user.role)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut, summary="获取当前用户信息")
async def get_me(current_user: User = Depends(get_current_user)):
    """通过 token 获取当前登录用户信息"""
    return current_user


@router.post("/set-monitor/{username}", summary="设置/取消纪律委员")
async def set_monitor(
    username: str,
    action: str = "promote",
    current_user: User = Depends(require_counselor),
    db: Session = Depends(get_db),
):
    """辅导员将学生设为纪律委员，或取消纪律委员身份"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.role == "counselor":
        raise HTTPException(status_code=400, detail="不能修改辅导员角色")

    if action == "promote":
        user.role = "monitor"
        db.commit()
        return {"message": f"已将 {user.name} 设为纪律委员", "role": "monitor"}
    elif action == "demote":
        user.role = "student"
        db.commit()
        return {"message": f"已取消 {user.name} 的纪律委员身份", "role": "student"}
    else:
        raise HTTPException(status_code=400, detail="action 参数无效，使用 promote 或 demote")


@router.get("/monitors", summary="获取所有纪律委员列表")
async def list_monitors(
    current_user: User = Depends(require_counselor),
    db: Session = Depends(get_db),
):
    monitors = db.query(User).filter(User.role == "monitor").all()
    return [UserOut.model_validate(m) for m in monitors]


@router.get("/students", summary="获取所有学生列表（含纪律委员）")
async def list_students(
    current_user: User = Depends(require_counselor),
    db: Session = Depends(get_db),
):
    students = db.query(User).filter(User.role.in_(["student", "monitor"])).all()
    return [UserOut.model_validate(s) for s in students]
