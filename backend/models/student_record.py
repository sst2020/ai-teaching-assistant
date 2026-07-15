"""
学生记录模型

记录学生基本信息及其作业关联的独立表。
"""
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import TimestampMixin
from core.database import Base


class StudentRecord(Base, TimestampMixin):
    """
    学生记录模型 - 独立的学生信息与作业关联表。

    字段:
        id: 主键
        name: 学生姓名
        student_id: 学号 (唯一)
        password_hash: bcrypt 哈希后的密码
        assignment_number: 作业编号
    """
    __tablename__ = "student_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="学生姓名"
    )

    student_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="学号"
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt 哈希后的密码"
    )

    assignment_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="作业编号"
    )

    def __repr__(self) -> str:
        return (
            f"<StudentRecord(id={self.id}, student_id='{self.student_id}', "
            f"name='{self.name}', assignment_number='{self.assignment_number}')>"
        )
