from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import models, schema, crud
from .database import engine, get_db, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="学生成绩管理系统 - ORM 版")

# 学生相关接口

@app.get("/students", response_model=List[schema.StudentResponse])
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_students(db, skip=skip, limit=limit)

@app.get("/students/{student_id}", response_model=schema.StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student

@app.post("/students", response_model=schema.StudentResponse, status_code=201)
def create_student(student: schema.StudentBase, db: Session = Depends(get_db)):
    return crud.create_student(db, student)

@app.put("/students/{student_id}", response_model=schema.StudentResponse)
def edit_student(student_id: int, data: schema.StudentBase, db: Session = Depends(get_db)):
    student = crud.update_student(db, student_id, data)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student

@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.delete_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    

# 课程相关接口

@app.get("/courses", response_model=List[schema.CourseResponse])
def list_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_courses(db, skip=skip, limit=limit)

@app.get("/courses/{course_id}", response_model=schema.CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = crud.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return course

@app.post("/courses", response_model=schema.CourseResponse, status_code=201)
def create_course(course: schema.CourseCreate, db: Session = Depends(get_db)):
    return crud.create_course(db, course)

@app.get("/courses/{course_id}/rankings", response_model=schema.CourseRankingResponse)
def get_course_ranking(course_id: int, db: Session = Depends(get_db)):
    ranking = crud.get_course_ranking(db, course_id)
    if not ranking:
        raise HTTPException(status_code=404, detail="课程不存在")
    return ranking

# 学生选课&成绩相关接口

@app.post("/enrollments", response_model=schema.EnrollmentResponse, status_code=201)
def enroll_student(enrollment: schema.EnrollmentCreate, db: Session = Depends(get_db)):
    return crud.enroll_student(db, enrollment)

@app.put("/enrollments/{enrollment_id}/score", response_model=schema.EnrollmentResponse)
def set_score(enrollment_id: int, score_update: schema.ScoreUpdate, db: Session = Depends(get_db)):
    enrollment = crud.set_score(db, enrollment_id, score_update)
    if not enrollment:
        raise HTTPException(status_code=404, detail="选课记录不存在")
    return enrollment

# 统计相关接口

@app.get("/students/{student_id}/grades")
def get_student_grades(student_id: int, db: Session = Depends(get_db)):
    result = crud.get_student_grade_summary(db, student_id)
    if not result:
        raise HTTPException(status_code=404, detail="学生不存在")
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
