# Web 后端第三次课后问答题

## 第 1 题：什么是 ORM？使用 ORM 相比纯 SQL 有什么优点和缺点？

ORM（Object Relational Mapping，对象关系映射）是一种把关系型数据库中的表、字段和记录映射为编程语言中的类、属性和对象的技术。例如，数据库中的 `students` 表可以映射为 Python 的 `Student` 类，一条学生记录可以表示为一个 `Student` 对象。开发者可以通过操作对象完成数据库读写，而不必为每个操作直接编写 SQL。

使用 ORM 的优点包括：

1. 代码更直观，可以使用类、对象和属性操作数据，提高可读性和可维护性。
2. 减少重复 SQL，提高增删改查功能的开发效率。
3. ORM 通常会自动进行参数绑定，能够降低 SQL 注入风险。
4. 对不同数据库具有一定的兼容性，更换数据库时业务代码改动相对较少。
5. 可以通过 `relationship` 等功能方便地访问关联对象。

使用 ORM 的缺点包括：

1. ORM 自动生成的 SQL 不一定是性能最优的。
2. 复杂查询仍然要求开发者理解 SQL、索引和执行计划。
3. 使用不当可能产生 N+1 查询、加载过多数据等性能问题。
4. ORM 增加了额外的学习成本和运行时开销。
5. 部分数据库特有功能难以通过通用 ORM API 完整表达。

## 第 2 题：ForeignKey 和 relationship 有什么区别？

`ForeignKey` 是数据库层面的外键约束，用于指定当前字段引用另一张表的字段：

```python
student_id: Mapped[int] = mapped_column(
    ForeignKey("students.id"),
    nullable=False,
)
```

它负责建立数据库表之间的引用关系、维护数据完整性，并为关联查询提供连接字段。

`relationship` 是 SQLAlchemy ORM 层面的对象关系，用于在 Python 对象之间导航：

```python
student: Mapped["Student"] = relationship(
    back_populates="enrollments"
)
```

定义后可以直接访问 `enrollment.student` 和 `student.enrollments`。

如果只写 `ForeignKey` 而不写 `relationship`，数据库外键约束仍然存在，也仍然可以使用 `join()` 查询关联数据，但是不能直接通过对象属性访问关联对象，需要手动编写关联查询。因此，`ForeignKey` 负责数据库约束，`relationship` 负责 ORM 对象之间的导航。

## 第 3 题：db.add()、db.commit()、db.refresh() 的作用和顺序

典型执行顺序如下：

```python
student = Student(name="张三", email="zhangsan@example.com")

db.add(student)
db.commit()
db.refresh(student)
```

`db.add()` 将对象加入当前 Session。此时对象通常只是进入待插入状态，SQLAlchemy 不一定立即执行 `INSERT`。

`db.commit()` 提交当前事务。提交前 SQLAlchemy 会先执行 `flush`，把待处理的 `INSERT`、`UPDATE` 和 `DELETE` 发送到数据库，然后提交事务。提交失败时通常需要调用 `db.rollback()`。

`db.refresh()` 会重新从数据库查询当前记录，并刷新 ORM 对象中的属性。新增数据后调用它，可以取得自增主键、数据库默认值、`server_default` 或触发器生成的字段。主键有时在 `flush()` 后就可以取得，因此 `refresh()` 并非任何情况下都必需，但它可以确保对象中的数据与数据库当前值一致。

## 第 4 题：FastAPI 的依赖注入与 get_db()

依赖注入是指路由函数声明自己需要的资源，由 FastAPI 负责创建、传入和清理这些资源。数据库会话依赖可以定义为：

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

路由通过 `Depends` 使用这个依赖：

```python
@app.get("/students")
def list_students(db: Session = Depends(get_db)):
    return db.scalars(select(Student)).all()
```

一次请求中，FastAPI 首先调用 `get_db()` 创建 Session，执行到 `yield db` 时把 Session 传给路由函数。请求处理完成或发生异常后，FastAPI 会继续执行 `finally`，调用 `db.close()` 释放数据库连接。这样可以避免每个路由重复编写创建和关闭 Session 的代码，也能防止异常情况下连接没有被释放。

## 第 5 题：一对多和多对多关系映射

学生、课程和选课记录可以定义为：

```python
from typing import Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="student"
    )


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="course"
    )


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id"), nullable=False
    )
    score: Mapped[Optional[float]]
    grade: Mapped[Optional[str]]

    student: Mapped["Student"] = relationship(
        back_populates="enrollments"
    )
    course: Mapped["Course"] = relationship(
        back_populates="enrollments"
    )
```

这里包含两组一对多关系：一个学生对应多条 `Enrollment`，一门课程也对应多条 `Enrollment`。从整体上看，学生和课程通过 `Enrollment` 构成多对多关系。

`ForeignKey` 建立数据库外键约束；`relationship` 建立 Python 对象之间的关联属性；`back_populates` 声明关系两端互相对应。由于选课关系还需要保存成绩和等级，所以应该使用独立的 `Enrollment` 关联模型，而不是只使用简单的 `secondary` 中间表。

## 第 6 题：查询选择“Python 程序设计”的学生及成绩

```python
from sqlalchemy import select
from sqlalchemy.orm import Session


def get_course_students(db: Session, course_name: str):
    stmt = (
        select(
            Student.id,
            Student.name,
            Student.email,
            Enrollment.score,
            Enrollment.grade,
        )
        .join(Enrollment, Student.id == Enrollment.student_id)
        .join(Course, Course.id == Enrollment.course_id)
        .where(Course.name == course_name)
        .order_by(Enrollment.score.desc())
    )

    rows = db.execute(stmt).all()

    return [
        {
            "student_id": row.id,
            "student_name": row.name,
            "email": row.email,
            "score": row.score,
            "grade": row.grade,
        }
        for row in rows
    ]


students = get_course_students(db, "Python 程序设计")
```

查询先连接 `Student`、`Enrollment` 和 `Course` 三张表，再通过课程名称筛选记录。`order_by(Enrollment.score.desc())` 可以让成绩按分数从高到低排列。

## 第 7 题：ORM 中的事务管理

事务用于保证一组数据库操作具有原子性，即这些操作要么全部成功，要么全部失败。`commit()` 用于提交事务，使修改永久保存；`rollback()` 用于在发生异常时撤销当前事务中尚未提交的修改，并恢复 Session 的可用状态。

同时创建学生并完成选课时，应把两个操作放在同一个事务中：

```python
def create_student_and_enroll(db: Session, student_data, course_id: int):
    try:
        student = Student(
            name=student_data.name,
            email=student_data.email,
        )
        db.add(student)

        # 执行 INSERT 并取得学生 ID，但暂不提交事务
        db.flush()

        enrollment = Enrollment(
            student_id=student.id,
            course_id=course_id,
        )
        db.add(enrollment)

        db.commit()
        db.refresh(student)
        db.refresh(enrollment)
        return student, enrollment

    except Exception:
        db.rollback()
        raise
```

关键是中途不要提前调用 `commit()`。`flush()` 可以把 SQL 发送到数据库并取得学生 ID，但不会单独提交事务。也可以使用事务上下文：

```python
with SessionLocal() as db:
    with db.begin():
        student = Student(name="张三", email="zhangsan@example.com")
        db.add(student)
        db.flush()

        db.add(Enrollment(student_id=student.id, course_id=1))
```

退出 `db.begin()` 时会自动提交；发生异常时会自动回滚。

## 第 8 题：create_all() 与 Alembic 的区别

```python
Base.metadata.create_all(bind=engine)
```

SQLAlchemy 加载完所有模型后，可以调用这行代码创建尚不存在的数据表。它适合教学项目、原型项目、自动化测试和首次创建简单数据库。

`create_all()` 主要负责创建缺失的表，通常不会自动修改已有表结构。例如给模型新增一列后，再次调用 `create_all()` 不会可靠地把新列添加到旧表。

Alembic 是数据库版本迁移工具，可以生成迁移脚本，新增、删除或修改字段，创建索引，记录数据库版本，并支持数据库结构的升级和回滚。小型教学项目可以使用 `create_all()`；需要长期维护或部署到生产环境的项目应使用 Alembic。

## 第 9 题：启动事件调用与模块级调用的区别

如果在 `database.py` 模块级别直接调用：

```python
Base.metadata.create_all(bind=engine)
```

那么只要导入模块就会立即连接数据库并执行建表。这会产生导入副作用；单元测试或脚本仅导入配置时也会操作数据库；模型尚未全部导入时还可能造成元数据不完整。

在 FastAPI 启动阶段调用，执行时机和应用生命周期更加明确：

```python
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
```

因此启动阶段调用比模块级调用更合适。现代 FastAPI 更推荐使用 `lifespan`：

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
```

正式生产项目最好在部署阶段使用 Alembic 执行迁移，而不是让每个应用进程启动时修改数据库结构。

## 第 10 题：response_model 和 from_attributes

`response_model` 用于声明接口响应的数据结构：

```python
@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    return db.get(Student, student_id)
```

它可以校验接口返回的数据、自动生成 OpenAPI 和 Swagger 文档、将数据序列化为 JSON、过滤响应模型中未声明的字段，并保证接口响应结构稳定。

Pydantic v2 可以这样配置：

```python
from pydantic import BaseModel, ConfigDict


class StudentResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)
```

`from_attributes=True` 表示 Pydantic 可以从 `student.id`、`student.name` 等对象属性中读取字段，而不要求返回值必须是字典。旧版 Pydantic 中对应的配置是 `orm_mode = True`。如果不设置，直接返回 SQLAlchemy ORM 对象时，Pydantic 可能无法正确解析对象并产生响应验证错误，除非开发者先手动把 ORM 对象转换为字典。
