"""
认证服务：JWT 生成/验证 + 密码加密
"""

from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import User

# Bearer token 提取器
security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """加密密码"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))


def create_token(user_id: int, username: str, role: str) -> str:
    """生成 JWT token"""
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """解析 JWT token"""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的认证信息")


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """依赖注入：获取当前登录用户"""
    if not credentials:
        raise HTTPException(status_code=401, detail="请先登录")

    payload = decode_token(credentials.credentials)
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def require_counselor(current_user: User = Depends(get_current_user)) -> User:
    """依赖注入：要求辅导员角色"""
    if current_user.role != "counselor":
        raise HTTPException(status_code=403, detail="无权限，仅辅导员可操作")
    return current_user


def require_monitor(current_user: User = Depends(get_current_user)) -> User:
    """依赖注入：要求纪律委员角色"""
    if current_user.role not in ("monitor", "counselor"):
        raise HTTPException(status_code=403, detail="无权限，仅纪律委员或辅导员可操作")
    return current_user


def init_counselor_account(db: Session):
    """初始化预设辅导员账号（如果不存在）"""
    existing = db.query(User).filter(User.username == settings.COUNSELOR_USERNAME).first()
    if not existing:
        counselor = User(
            username=settings.COUNSELOR_USERNAME,
            password_hash=hash_password(settings.COUNSELOR_PASSWORD),
            name=settings.COUNSELOR_NAME,
            role="counselor",
        )
        db.add(counselor)
        db.commit()
        print(f"✅ 预设辅导员账号已创建: {settings.COUNSELOR_USERNAME}")
    else:
        print(f"ℹ️  辅导员账号已存在: {settings.COUNSELOR_USERNAME}")
