"""
花名册导入脚本
从CSV文件导入学生花名册数据到class_rosters表
"""

import csv
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import ClassRoster, Base

# 创建表
Base.metadata.create_all(bind=engine)


def import_roster_from_csv(csv_path: str):
    """从CSV导入花名册"""
    db: Session = SessionLocal()

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            # 跳过前4行（标题行）
            for _ in range(4):
                next(f)

            reader = csv.reader(f)
            imported_count = 0
            skipped_count = 0

            for row in reader:
                if len(row) < 21:  # 确保行数据完整
                    continue

                # 解析CSV所有字段
                student_id = row[2].strip()  # 学号
                name = row[3].strip()  # 姓名
                gender = row[4].strip()  # 性别
                ethnicity = row[5].strip()  # 民族
                political_status = row[6].strip()  # 政治面貌
                id_card = row[7].strip()  # 身份证号
                phone = row[8].strip()  # 本人电话
                hometown = row[9].strip()  # 生源地
                home_address = row[10].strip()  # 家庭实际居住地址
                parent_name = row[11].strip()  # 家长姓名
                parent_phone = row[12].strip()  # 家长手机号码
                dorm_nickname = row[13].strip()  # 实际学校居住地址（俗称）
                dorm_address = row[14].strip()  # 实际居住标准地址
                major = row[15].strip()  # 所属院系
                education_level = row[16].strip()  # 层次
                grade = row[17].strip()  # 年级
                specialty = row[18].strip()  # 专业
                class_name = row[19].strip()  # 年级专业班级
                counselor = row[20].strip()  # 辅导员
                remark = row[21].strip() if len(row) > 21 else ""  # 备注

                if not student_id or not name:
                    skipped_count += 1
                    continue

                # 检查是否已存在
                existing = db.query(ClassRoster).filter(
                    ClassRoster.student_id == student_id
                ).first()

                if existing:
                    # 更新现有记录
                    existing.name = name
                    existing.gender = gender
                    existing.ethnicity = ethnicity
                    existing.political_status = political_status
                    existing.id_card = id_card
                    existing.phone = phone
                    existing.hometown = hometown
                    existing.home_address = home_address
                    existing.parent_name = parent_name
                    existing.parent_phone = parent_phone
                    existing.dorm_nickname = dorm_nickname
                    existing.dorm_address = dorm_address
                    existing.major = major
                    existing.education_level = education_level
                    existing.grade = grade
                    existing.specialty = specialty
                    existing.class_name = class_name
                    existing.counselor = counselor
                    existing.remark = remark
                    print(f"更新: {student_id} {name}")
                else:
                    # 创建新记录
                    roster = ClassRoster(
                        student_id=student_id,
                        name=name,
                        gender=gender,
                        ethnicity=ethnicity,
                        political_status=political_status,
                        id_card=id_card,
                        phone=phone,
                        hometown=hometown,
                        home_address=home_address,
                        parent_name=parent_name,
                        parent_phone=parent_phone,
                        dorm_nickname=dorm_nickname,
                        dorm_address=dorm_address,
                        major=major,
                        education_level=education_level,
                        grade=grade,
                        specialty=specialty,
                        class_name=class_name,
                        counselor=counselor,
                        remark=remark
                    )
                    db.add(roster)
                    print(f"导入: {student_id} {name}")

                imported_count += 1

            db.commit()
            print(f"\n导入完成！")
            print(f"成功导入/更新: {imported_count} 条")
            print(f"跳过: {skipped_count} 条")

    except Exception as e:
        db.rollback()
        print(f"导入失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    csv_file = "/Users/mantou/Desktop/学生工作一站式平台/张罗怡-外国语言与文化学院2026年3月带班人数花名册表0309.csv"

    print(f"开始导入花名册: {csv_file}")
    import_roster_from_csv(csv_file)
