#!/usr/bin/env python3
"""
初始化测试数据脚本
创建三种测试账号：管理员、教师、学生
"""

import asyncio
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, '.')

from sqlalchemy import select
from core.database import async_session_factory
from models.user import User
from models.student import Student
from models.teacher import Teacher
from utils.password import hash_password


async def init_test_data():
    """初始化测试数据"""
    
    async with async_session_factory() as session:
        # 检查是否已有测试数据
        result = await session.execute(
            select(User).where(User.student_id.in_([
                "0000000001",  # 管理员
                "0000000002",  # 教师
                "0000000003",  # 学生
            ]))
        )
        existing = result.scalars().all()
        if existing:
            print("测试账号已存在，跳过初始化")
            for user in existing:
                print(f"  - {user.role}: {user.student_id} ({user.name})")
            return

        # 1. 创建管理员
        admin_user = User(
            student_id="0000000001",
            email="admin@test.com",
            password_hash=hash_password("Admin123456"),
            name="系统管理员",
            role="admin",
            is_active=True,
        )
        session.add(admin_user)
        await session.flush()
        print(f"✓ 管理员: 0000000001 / Admin123456")

        # 2. 创建教师
        teacher_user = User(
            student_id="0000000002",
            email="teacher@test.com",
            password_hash=hash_password("Teacher123456"),
            name="张老师",
            role="teacher",
            is_active=True,
        )
        session.add(teacher_user)
        await session.flush()
        
        # 创建教师详情
        teacher_profile = Teacher(
            user_id=teacher_user.id,
            teacher_id="T2024000001",
            name="张老师",
            email="teacher@test.com",
            department="计算机学院",
            title="副教授",
            hire_date=datetime.now(),
        )
        session.add(teacher_profile)
        print(f"✓ 教师: 0000000002 / Teacher123456")

        # 3. 创建学生
        student_user = User(
            student_id="0000000003",
            email="student@test.com",
            password_hash=hash_password("Student123456"),
            name="学生小明",
            role="student",
            is_active=True,
        )
        session.add(student_user)
        await session.flush()
        
        # 创建学生详情
        student_profile = Student(
            user_id=student_user.id,
            student_number="2024001001",
            name="学生小明",
            email="student@test.com",
            major="计算机科学与技术",
            grade="2024",
            class_name="计科2401",
            enrollment_year=2024,
        )
        session.add(student_profile)
        print(f"✓ 学生: 0000000003 / Student123456")

        await session.commit()
        print("\n✅ 测试数据初始化完成")
        print("\n测试账号信息：")
        print("  管理员: 0000000001 / Admin123456")
        print("  教师:   0000000002 / Teacher123456")
        print("  学生:   0000000003 / Student123456")


if __name__ == "__main__":
    print("=" * 50)
    print("AI Teaching Assistant - 初始化测试数据")
    print("=" * 50)
    print()
    
    try:
        asyncio.run(init_test_data())
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
