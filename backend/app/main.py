"""
FastAPI 应用入口
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import init_db
from .routers import achievements, export, feedback


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    init_db()
    print(f"✅ {settings.APP_NAME} 启动成功")
    yield
    print("👋 应用关闭")


app = FastAPI(
    title=settings.APP_NAME,
    description="解决辅导员录入数据累、学生填表烦的智能工具",
    version="0.1.0",
    lifespan=lifespan,
)

# ---- CORS 中间件 ----
cors_origins = list(settings.CORS_ORIGINS)
if settings.CORS_EXTRA_ORIGINS:
    cors_origins.extend([o.strip() for o in settings.CORS_EXTRA_ORIGINS.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- 静态文件（上传的证书图片） ----
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ---- 注册路由 ----
app.include_router(
    achievements.router,
    prefix=f"{settings.API_PREFIX}/achievements",
    tags=["科研与比赛成果"],
)
app.include_router(
    export.router,
    prefix=f"{settings.API_PREFIX}/export",
    tags=["数据导出"],
)
app.include_router(
    feedback.router,
    prefix=f"{settings.API_PREFIX}/feedback",
    tags=["树洞（匿名反馈）"],
)


@app.get("/", tags=["健康检查"])
async def root():
    return {"message": f"{settings.APP_NAME} 运行中", "version": "0.1.0"}


@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "healthy"}
