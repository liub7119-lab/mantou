"""
批量为花名册中的学生创建账号
密码统一设置为 123456
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, ClassRoster
from app.services.auth_service import hash_password


def create_student_accounts():
    """为所有花名册学生创建账号"""
    db: Session = SessionLocal()

    try:
        # 获取所有花名册学生
        rosters = db.query(ClassRoster).all()

        created_count = 0
        skipped_count = 0

        for roster in rosters:
            # 检查账号是否已存在
            existing = db.query(User).filter(
                User.username == roster.student_id
            ).first()

            if existing:
                print(f"跳过（已存在）: {roster.student_id} {roster.name}")
                skipped_count += 1
                continue

            # 创建新账号
            hashed_password = hash_password("123456")
            user = User(
                username=roster.student_id,
                password_hash=hashed_password,
                name=roster.name,
                role="student",
                class_name=roster.class_name,
                major=roster.major
            )
            db.add(user)
            print(f"创建账号: {roster.student_id} {roster.name} (密码: 123456)")
            created_count += 1

        db.commit()

        print(f"\n批量创建完成！")
        print(f"成功创建: {created_count} 个账号")
        print(f"跳过: {skipped_count} 个账号")
        print(f"\n所有学生账号密码统一为: 123456")

    except Exception as e:
        db.rollback()
        print(f"创建失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("开始为花名册学生批量创建账号...")
    print("=" * 60)
    create_student_accounts()
