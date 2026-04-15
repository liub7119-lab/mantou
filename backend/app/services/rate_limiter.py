"""
简易速率限制器（内存级）
基于 IP 地址限制请求频率，防止脚本攻击
"""

import time
from collections import defaultdict, deque
from functools import wraps

from fastapi import HTTPException, Request


class RateLimiter:
    """
    滑动窗口速率限制器
    用法：rate_limiter = RateLimiter(max_requests=3, window_seconds=3600)
    """

    def __init__(self, max_requests: int = 3, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # IP -> deque of timestamps
        self._requests: dict[str, deque] = defaultdict(deque)

    def _clean_old(self, ip: str):
        """清理过期的请求记录"""
        now = time.time()
        q = self._requests[ip]
        while q and now - q[0] > self.window_seconds:
            q.popleft()
        # 如果队列空了，删除键释放内存
        if not q:
            self._requests.pop(ip, None)

    def check(self, ip: str) -> dict:
        """
        检查是否允许请求
        返回 {"allowed": bool, "remaining": int, "reset_in": int}
        """
        self._clean_old(ip)
        q = self._requests.get(ip, deque())
        remaining = self.max_requests - len(q)
        reset_in = int(self.window_seconds - (time.time() - q[0])) if q else self.window_seconds

        if len(q) >= self.max_requests:
            return {"allowed": False, "remaining": 0, "reset_in": reset_in}
        return {"allowed": True, "remaining": remaining, "reset_in": reset_in}

    def record(self, ip: str):
        """记录一次请求"""
        self._requests[ip].append(time.time())


# ── 全局实例：树洞投递限制（每 IP 每小时 3 条） ──
feedback_limiter = RateLimiter(max_requests=3, window_seconds=3600)
