"""
迁移脚本：为class_rosters表添加新字段
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine

def migrate_roster_table():
    """为class_rosters表添加新字段"""

    new_columns = [
        "ALTER TABLE class_rosters ADD COLUMN ethnicity VARCHAR(20) DEFAULT ''",
        "ALTER TABLE class_rosters ADD COLUMN political_status VARCHAR(30) DEFAULT ''",
        "ALTER TABLE class_rosters ADD COLUMN id_card VARCHAR(30) DEFAULT ''",
        "ALTER TABLE class_rosters ADD COLUMN hometown VARCHAR(100) DEFAULT ''",
        "ALTER TABLE class_rosters ADD COLUMN home_address VARCHAR(300) DEFAULT ''",
        "ALTER TABLE class_rosters ADD COLUMN parent_name VARCHAR(50) DEFAULT ''",
        "ALTER TABLE class_rosters ADD COLUMN parent_phone VARCHAR(20) DEFAULT ''",
        "ALTER TABLE class_rosters ADD COLUMN dorm_nickname VARCHAR(50) DEFAULT ''",
        "ALTER TABLE class_rosters ADD COLUMN dorm_address VARCHAR(200) DEFAULT ''",
        "ALTER TABLE class_rosters ADD COLUMN education_level VARCHAR(20) DEFAULT ''",
        "ALTER TABLE class_rosters ADD COLUMN grade VARCHAR(20) DEFAULT ''",
        "ALTER TABLE class_rosters ADD COLUMN specialty VARCHAR(100) DEFAULT ''",
        "ALTER TABLE class_rosters ADD COLUMN remark VARCHAR(500) DEFAULT ''",
    ]

    with engine.connect() as conn:
        for sql in new_columns:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"✓ 执行成功: {sql}")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print(f"⊙ 字段已存在，跳过: {sql}")
                else:
                    print(f"✗ 执行失败: {sql}")
                    print(f"  错误: {e}")

    print("\n迁移完成！")


if __name__ == "__main__":
    print("开始迁移class_rosters表...")
    print("=" * 60)
    migrate_roster_table()
