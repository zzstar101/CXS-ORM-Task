from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class StudentBase(BaseModel):
    name: str
    email: str

class StudentResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
        
class CourseCreate(BaseModel):
    name: str
    teacher: str
    credits: float = 1.0
    
class CourseResponse(BaseModel):
    id: int
    name: str
    teacher: str
    credits: float

    class Config:
        from_attributes = True
        
class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int

class ScoreUpdate(BaseModel):
    score: float
    
class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    grade: Optional[str] = None
    score: Optional[float] = None

    class Config:
        from_attributes = True

class CourseRankingItem(BaseModel):
    student_id: int
    student_name: str
    email: str
    score: Optional[float] = None
    grade: Optional[str] = None

class CourseRankingResponse(BaseModel):
    course_id: int
    course_name: str
    students: List[CourseRankingItem]
    
class StudentWithCourses(StudentResponse):
    enrollments: List[EnrollmentResponse] = []
