"""
数据库连接与会话管理
使用 SQLite 作为轻量级数据库
"""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


# SQLite 数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 多线程支持
    echo=settings.DEBUG,  # DEBUG 模式下打印 SQL
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 声明式基类
class Base(DeclarativeBase):
    pass


def get_db():
    """
    FastAPI 依赖注入：获取数据库会话
    用法: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """创建所有表（如果不存在）"""
    Base.metadata.create_all(bind=engine)
    _migrate_add_columns()


def _migrate_add_columns():
    """自动添加新增的列（SQLite 不支持 ALTER COLUMN，但支持 ADD COLUMN）"""
    migrations = [
        ("attendance_records", "classroom_photos", "TEXT DEFAULT ''"),
    ]
    with engine.connect() as conn:
        insp = inspect(engine)
        for table, column, col_type in migrations:
            if table not in insp.get_table_names():
                continue
            existing = [c["name"] for c in insp.get_columns(table)]
            if column not in existing:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                conn.commit()
