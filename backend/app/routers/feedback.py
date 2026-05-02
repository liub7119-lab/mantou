"""
树洞（匿名反馈）路由
处理：匿名投递 → AI情绪分析 → 分类归档 → 双向对话
"""

import secrets
import string
import hashlib
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Feedback, FeedbackReply
from ..schemas import (
    FeedbackCreate,
    FeedbackDetail,
    FeedbackOut,
    FeedbackReplyCreate,
    FeedbackReplyOut,
    MessageResponse,
)
from ..services.emotion_service import analyze_emotion
from ..services.rate_limiter import feedback_limiter

router = APIRouter()


def _generate_anonymous_id() -> str:
    """生成可爱的随机昵称，如 树洞·冒泡的小水獭"""
    adjectives = [
        "冒泡的", "迷路的", "打盹的", "偷吃的", "蹦跶的",
        "发呆的", "害羞的", "圆滚滚的", "毛茸茸的", "软乎乎的",
        "眯眼的", "翻肚皮的", "踮脚的", "哼歌的", "吹泡泡的",
        "晒太阳的", "追蝴蝶的", "啃竹子的", "揉眼睛的", "打哈欠的",
        "藏尾巴的", "摇耳朵的", "舔爪子的", "转圈圈的", "挠下巴的",
        "叠罗汉的", "蹭树皮的", "滚草地的", "捂耳朵的", "歪头的",
    ]
    animals = [
        "小水獭", "小熊猫", "小刺猬", "小企鹅", "小海豹",
        "小柴犬", "小仓鼠", "小树懒", "小浣熊", "小兔叽",
        "小鹦鹉", "小猫咪", "小鸭鸭", "小松鼠", "小狐狸",
        "小河马", "小考拉", "小龙猫", "小海马", "小麋鹿",
        "小章鱼", "小水母", "小土拨鼠", "小羊驼", "小北极熊",
        "小海獭", "小花鹿", "小白鲸", "小熊蜂", "小胖达",
    ]
    adj = secrets.choice(adjectives)
    animal = secrets.choice(animals)
    suffix = secrets.choice(string.digits) + secrets.choice(string.digits)
    return f"树洞·{adj}{animal}{suffix}"


# ──────────────────────────────────────────────
# 学生端：投递反馈
# ──────────────────────────────────────────────
@router.post("/submit", response_model=FeedbackOut, summary="匿名投递反馈")
async def submit_feedback(request: Request, data: FeedbackCreate, db: Session = Depends(get_db)):
    """
    学生匿名提交反馈 → 速率限制检查 → AI 情绪分析 → 存入数据库
    限制：每个 IP 每小时最多 3 条
    """
    # 速率限制
    client_ip = request.headers.get("x-forwarded-for", request.client.host).split(",")[0].strip()
    check = feedback_limiter.check(client_ip)
    if not check["allowed"]:
        raise HTTPException(
            status_code=429,
            detail=f"投递过于频繁，每小时最多 3 条。请 {check['reset_in'] // 60} 分钟后再试",
        )

    # 生成唯一匿名 ID
    anonymous_id = _generate_anonymous_id()
    while db.query(Feedback).filter(Feedback.anonymous_id == anonymous_id).first():
        anonymous_id = _generate_anonymous_id()

    # AI 情绪分析
    emotion = await analyze_emotion(data.content)

    feedback = Feedback(
        anonymous_id=anonymous_id,
        content=data.content,
        category=data.category,
        emotion_score=emotion["score"],
        emotion_label=emotion["label"],
        is_urgent=emotion["score"] <= 3,
        status="pending",
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    # 投递成功，记录本次请求用于限流计数
    feedback_limiter.record(client_ip)

    return feedback


# ──────────────────────────────────────────────
# 学生端：通过匿名 ID 查看自己的反馈和回复
# ──────────────────────────────────────────────
@router.get("/mine/{anonymous_id}", response_model=FeedbackDetail, summary="查看我的反馈")
async def get_my_feedback(anonymous_id: str, db: Session = Depends(get_db)):
    """学生通过匿名 ID 查看自己的反馈详情和对话"""
    feedback = (
        db.query(Feedback)
        .options(joinedload(Feedback.replies))
        .filter(Feedback.anonymous_id == anonymous_id)
        .first()
    )
    if not feedback:
        raise HTTPException(status_code=404, detail="未找到该反馈，请检查匿名 ID")
    return feedback


# ──────────────────────────────────────────────
# 学生端：追加回复
# ──────────────────────────────────────────────
@router.post("/mine/{anonymous_id}/reply", response_model=FeedbackReplyOut, summary="学生追加回复")
async def student_reply(anonymous_id: str, data: FeedbackReplyCreate, db: Session = Depends(get_db)):
    """学生通过匿名 ID 追加回复"""
    feedback = db.query(Feedback).filter(Feedback.anonymous_id == anonymous_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="未找到该反馈")

    reply = FeedbackReply(
        feedback_id=feedback.id,
        content=data.content,
        is_counselor=False,  # 学生端强制为非辅导员
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply


# ──────────────────────────────────────────────
# 管理端：查看反馈列表
# ──────────────────────────────────────────────
@router.get("/admin/list", response_model=List[FeedbackOut], summary="管理端 - 反馈列表")
async def list_feedbacks(
    category: Optional[str] = None,
    status: Optional[str] = None,
    urgent_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    辅导员查看反馈列表
    紧急预警自动置顶（按 is_urgent DESC, emotion_score ASC 排序）
    """
    query = db.query(Feedback)

    if category:
        query = query.filter(Feedback.category == category)
    if status:
        query = query.filter(Feedback.status == status)
    if urgent_only:
        query = query.filter(Feedback.is_urgent == True)

    # 紧急置顶 → 分数低的排前面 → 最新的排前面
    return (
        query
        .order_by(Feedback.is_urgent.desc(), Feedback.emotion_score.asc(), Feedback.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# ──────────────────────────────────────────────
# 管理端：查看反馈详情 + 对话
# ──────────────────────────────────────────────
@router.get("/admin/{feedback_id}", response_model=FeedbackDetail, summary="管理端 - 反馈详情")
async def get_feedback_detail(feedback_id: int, db: Session = Depends(get_db)):
    """辅导员查看某条反馈的详细内容和对话记录"""
    feedback = (
        db.query(Feedback)
        .options(joinedload(Feedback.replies))
        .filter(Feedback.id == feedback_id)
        .first()
    )
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    return feedback


# ──────────────────────────────────────────────
# 管理端：辅导员回复
# ──────────────────────────────────────────────
@router.post("/admin/{feedback_id}/reply", response_model=FeedbackReplyOut, summary="管理端 - 辅导员回复")
async def counselor_reply(feedback_id: int, data: FeedbackReplyCreate, db: Session = Depends(get_db)):
    """辅导员回复学生反馈"""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")

    reply = FeedbackReply(
        feedback_id=feedback.id,
        content=data.content,
        is_counselor=True,  # 管理端强制为辅导员
    )
    db.add(reply)

    # 更新反馈状态为"已回复"
    if feedback.status == "pending":
        feedback.status = "replied"

    db.commit()
    db.refresh(reply)
    return reply


# ──────────────────────────────────────────────
# 管理端：关闭反馈
# ──────────────────────────────────────────────
@router.patch("/admin/{feedback_id}/close", response_model=MessageResponse, summary="管理端 - 关闭反馈")
async def close_feedback(feedback_id: int, db: Session = Depends(get_db)):
    """辅导员关闭已处理的反馈"""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")

    feedback.status = "closed"
    db.commit()
    return MessageResponse(message="反馈已关闭")
