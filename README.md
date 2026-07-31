# 学生成绩管理系统（ORM 版）

基于 FastAPI、SQLAlchemy 2.0 和 SQLite 实现的学生成绩管理 REST API。项目使用 ORM 完成学生、课程和选课记录的数据建模，并通过 Pydantic 模型校验请求与序列化响应。

## 技术栈

- Python 3.12+
- FastAPI
- SQLAlchemy 2.0
- Pydantic
- SQLite
- Uvicorn
- uv（依赖与虚拟环境管理）

## 已实现功能

- 学生信息的新增、删除、修改、单个查询和分页列表查询
- 课程信息的新增、单个查询和分页列表查询
- 学生选课
- 录入分数，并自动换算为 A、B、C、D、F 等级
- 查询指定学生的课程成绩与按学分加权的平均分
- 查询指定课程的学生成绩排行
- 应用启动时自动创建数据库表
- Swagger 和 ReDoc 在线接口文档

## 项目结构

```text
CXS-ORM-Task/
├── src/
│   └── cxs_orm_task/
│       ├── crud.py       # 数据库增删改查和成绩统计
│       ├── database.py   # 数据库引擎、会话工厂和 Base 基类
│       ├── main.py       # FastAPI 应用与路由
│       ├── models.py     # SQLAlchemy ORM 模型
│       └── schema.py     # Pydantic 请求与响应模型
├── .python-version       # Python 版本配置
├── pyproject.toml        # 项目元数据与依赖
├── QA.md                 # 课后问答题答案
├── uv.lock               # 依赖锁定文件
└── README.md
```

## 数据模型

系统包含 3 个核心模型：

- `Student`：学生信息，包括姓名、邮箱和创建时间。
- `Course`：课程信息，包括课程名称、授课教师和学分。
- `Enrollment`：学生与课程之间的关联记录，包括分数和等级。

一个学生可以拥有多条选课记录，一门课程也可以拥有多条选课记录。`Student` 与 `Course` 通过中间模型 `Enrollment` 构成多对多关系。

## 快速启动

### 方式一：使用 uv（推荐）

安装 [uv](https://docs.astral.sh/uv/) 后，在项目根目录执行：

```bash
uv sync
uv run uvicorn cxs_orm_task.main:app --reload
```

### 方式二：使用 pip

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
pip install fastapi "sqlalchemy>=2.0" uvicorn
pip install -e .
uvicorn cxs_orm_task.main:app --reload
```

服务启动后可访问：

- Swagger 文档：<http://127.0.0.1:8000/docs>
- ReDoc 文档：<http://127.0.0.1:8000/redoc>

首次启动时，程序会在执行启动命令时所在的目录创建 `student_grades.db`，并自动创建所需数据表。建议始终从项目根目录启动服务。

## API 列表

### 学生管理

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/students?skip=0&limit=100` | 分页查询学生列表 |
| `GET` | `/students/{student_id}` | 查询指定学生 |
| `POST` | `/students` | 新增学生 |
| `PUT` | `/students/{student_id}` | 修改指定学生 |
| `DELETE` | `/students/{student_id}` | 删除指定学生 |

新增或修改学生的请求体示例：

```json
{
  "name": "张三",
  "email": "zhangsan@example.com"
}
```

### 课程管理

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/courses?skip=0&limit=100` | 分页查询课程列表 |
| `GET` | `/courses/{course_id}` | 查询指定课程 |
| `POST` | `/courses` | 新增课程 |
| `GET` | `/courses/{course_id}/rankings` | 查询课程成绩排行，按分数降序排列 |

新增课程的请求体示例：

```json
{
  "name": "Python 程序设计",
  "teacher": "陈老师",
  "credits": 3.0
}
```

课程成绩排行响应示例：

```json
{
  "course_id": 1,
  "course_name": "Python 程序设计",
  "students": [
    {
      "student_id": 1,
      "student_name": "张三",
      "email": "zhangsan@example.com",
      "score": 92.0,
      "grade": "A"
    }
  ]
}
```

已录入成绩的学生按分数从高到低排列，未录入成绩的学生排在列表末尾。

### 选课与成绩

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/enrollments` | 创建学生选课记录 |
| `PUT` | `/enrollments/{enrollment_id}/score` | 为选课记录录入或修改分数 |
| `GET` | `/students/{student_id}/grades` | 查询指定学生的全部成绩和加权平均分 |

学生选课请求体示例：

```json
{
  "student_id": 1,
  "course_id": 1
}
```

成功创建选课记录后，响应中的 `id` 是选课记录 ID，录入成绩时应将它填入 URL 的 `enrollment_id`，而不是填写学生 ID 或课程 ID。例如：

```json
{
  "id": 1,
  "student_id": 1,
  "course_id": 1,
  "grade": null,
  "score": null
}
```

录入成绩请求体示例：

```json
{
  "score": 92
}
```

学生成绩汇总响应示例：

```json
{
  "student_name": "张三",
  "courses": [
    {
      "name": "Python 程序设计",
      "credits": 3.0,
      "grade": "A",
      "score": 92.0
    }
  ],
  "total_credits": 3.0,
  "weighted_average_score": 92.0
}
```

## 成绩等级规则

| 分数范围 | 等级 |
| --- | --- |
| 大于等于 90 分 | A |
| 大于等于 80 分且小于 90 分 | B |
| 大于等于 70 分且小于 80 分 | C |
| 大于等于 60 分且小于 70 分 | D |
| 60 分以下 | F |

加权平均分的计算公式为：

```text
加权平均分 = Σ（课程分数 × 课程学分）÷ Σ（已录入成绩课程的学分）
```

## 使用流程示例

1. 调用 `POST /students` 创建学生，并记录响应中的学生 `id`。
2. 调用 `POST /courses` 创建课程，并记录响应中的课程 `id`。
3. 将前两步返回的 ID 作为 `student_id` 和 `course_id`，调用 `POST /enrollments`，并记录响应中的选课记录 `id`。
4. 将选课记录 ID 填入 `enrollment_id`，调用 `PUT /enrollments/{enrollment_id}/score` 录入成绩。
5. 调用 `GET /students/{student_id}/grades` 查询学生成绩汇总。

也可以直接在 Swagger 页面中按上述顺序测试接口。

## 开发说明

- 数据库连接地址在 `src/cxs_orm_task/database.py` 中配置。相对路径 `./student_grades.db` 以启动命令的当前工作目录为基准。
- SQLAlchemy 会话由 FastAPI 的 `Depends(get_db)` 依赖统一创建和关闭。
- 当前项目使用 `Base.metadata.create_all()` 建表，适合教学和开发演示；生产项目建议使用 Alembic 管理数据库版本迁移。
- `student_grades.db` 是本地运行数据，不建议提交到版本库。
- 当前请求模型尚未限制成绩必须在 0～100 之间，也尚未实现重复选课和关联对象存在性校验；调用接口时应传入有效数据。

## 后续可扩展功能

- 为学生选课增加重复选课校验
- 增加学生、课程和选课记录的外键存在性校验
- 增加成绩范围校验（0～100）
- 使用 Alembic 管理数据库迁移
- 增加自动化测试和统一异常处理
