from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from . import models, schema

def get_students(db: Session, skip: int = 0, limit: int = 100) -> List[models.Student]:
    stmt = select(models.Student).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())

def get_student(db: Session, student_id: int) -> Optional[models.Student]:
    return db.get(models.Student, student_id)

def create_student(db: Session, student: schema.StudentBase) -> models.Student:
    db_student = models.Student(name=student.name, email=student.email)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(db: Session, student_id: int, data: schema.StudentBase) -> Optional[models.Student]:
    student = db.get(models.Student, student_id)
    if not student:
        return None
    student.name = data.name
    student.email = data.email
    db.commit()
    db.refresh(student)
    return student

def delete_student(db: Session, student_id: int) -> bool:
    student = db.get(models.Student, student_id)
    if not student:
        return False
    db.delete(student)
    db.commit()
    return True

def get_courses(db: Session, skip: int = 0, limit: int = 100) -> List[models.Course]:
    stmt = select(models.Course).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())

def get_course(db: Session, course_id: int) -> Optional[models.Course]:
    return db.get(models.Course, course_id)

def create_course(db: Session, data: schema.CourseCreate) -> models.Course:
    db_course = models.Course(name=data.name, teacher=data.teacher, credits=data.credits)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_course_ranking(db: Session, course_id: int):
    course = db.get(models.Course, course_id)
    if not course:
        return None

    stmt = (
        select(
            models.Student.id,
            models.Student.name,
            models.Student.email,
            models.Enrollment.score,
            models.Enrollment.grade,
        )
        .join(
            models.Enrollment,
            models.Student.id == models.Enrollment.student_id,
        )
        .where(models.Enrollment.course_id == course_id)
        # 已录入的成绩按分数降序排列，未录入成绩的记录放在末尾
        .order_by(
            models.Enrollment.score.is_(None),
            models.Enrollment.score.desc(),
            models.Student.id.asc(),
        )
    )
    results = db.execute(stmt).all()

    return {
        "course_id": course.id,
        "course_name": course.name,
        "students": [
            {
                "student_id": student_id,
                "student_name": student_name,
                "email": email,
                "score": score,
                "grade": grade,
            }
            for student_id, student_name, email, score, grade in results
        ],
    }

def enroll_student(db: Session, data: schema.EnrollmentCreate) -> models.Enrollment:
    enrollment = models.Enrollment(student_id=data.student_id, course_id=data.course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment

def set_score(db: Session, enrollment_id: int, data: schema.ScoreUpdate) -> Optional[models.Enrollment]:
    enrollment = db.get(models.Enrollment, enrollment_id)
    if not enrollment:
        return None
    enrollment.score = data.score
    # Determine grade based on score
    if data.score >= 90:
        enrollment.grade = 'A'
    elif data.score >= 80:
        enrollment.grade = 'B'
    elif data.score >= 70:
        enrollment.grade = 'C'
    elif data.score >= 60:
        enrollment.grade = 'D'
    else:
        enrollment.grade = 'F'
    db.commit()
    db.refresh(enrollment)
    return enrollment

def get_student_grade_summary(db: Session, student_id: int):
    student = db.get(models.Student, student_id)
    if not student:
        return None
    
    stmt = (
        select(
            models.Course.name,
            models.Course.credits,
            models.Enrollment.grade,
            models.Enrollment.score
        )
        .join(models.Enrollment, models.Course.id == models.Enrollment.course_id)
        .where(models.Enrollment.student_id == student_id)
    )
    results = db.execute(stmt).all()
    
    total_credits = 0
    weighted_sum = 0
    for course_name, credits, grade, score in results:
        if score is not None:
            total_credits += credits
            weighted_sum += score * credits
            
        avg_score = round(weighted_sum / total_credits, 1) if total_credits > 0 else None
        
        return {
            "student_name": student.name,
            "courses": [{
                "name": r[0],
                "credits": r[1],
                "grade": r[2],
                "score": r[3]}
                        for r in results],
                        "total_credits": total_credits,
                        "weighted_average_score": avg_score
            }
