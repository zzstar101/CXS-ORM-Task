from datetime import datetime
from typing import Optional, List
from sqlalchemy import ForeignKey, String, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="学生姓名")
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="邮箱")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="student")
    
    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.name}')>"
    
class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="课程名称")
    teacher: Mapped[str] = mapped_column(String(50), nullable=False, comment="授课教师")
    credits: Mapped[float] = mapped_column(Float, default=1.0, comment="学分")
    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="course")
    
    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.name}')>"
    
class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, comment="学生ID")
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False, comment="课程ID")
    grade: Mapped[Optional[str]] = mapped_column(String(2), nullable=True, comment="等级 A/B/C/D/F")
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="考试成绩")
    student: Mapped["Student"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")
    
    def __repr__(self):
        return f"<Enrollment(student={self.student_id}, course={self.course_id}, score={self.score})>"