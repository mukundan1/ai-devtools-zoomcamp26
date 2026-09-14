from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from datetime import datetime, timezone
import os


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'kanban.db'}",
)

# The application only depends on SQLAlchemy's database abstraction.
# To upgrade to PostgreSQL later:
#
#   DATABASE_URL=postgresql+psycopg://user:password@localhost/kanban
#
# No route or repository code needs to change.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="todo", nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    status: Literal["todo", "doing", "done"] = "todo"


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: Literal["todo", "doing", "done"] | None = None
    position: int | None = Field(default=None, ge=0)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: Literal["todo", "doing", "done"]
    position: int
    created_at: datetime

    model_config = {"from_attributes": True}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def next_position(db: Session, status: str) -> int:
    tasks = db.scalars(
        select(Task).where(Task.status == status)
    ).all()

    return max((task.position for task in tasks), default=-1) + 1


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)

    with SessionLocal() as db:
        if not db.scalars(select(Task)).first():
            seed = [
                Task(
                    title="Welcome to your Kanban board",
                    description="Drag cards between columns.",
                    status="todo",
                    position=0,
                ),
                Task(
                    title="Connect the frontend",
                    description="The UI communicates with FastAPI.",
                    status="doing",
                    position=0,
                ),
                Task(
                    title="Prepare PostgreSQL migration",
                    description="Set DATABASE_URL when you are ready.",
                    status="done",
                    position=0,
                ),
            ]
            db.add_all(seed)
            db.commit()

    yield


app = FastAPI(
    title="Mini Kanban API",
    version="1.0.0",
    description="Database-agnostic Kanban API using SQLAlchemy.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/tasks", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.scalars(
        select(Task).order_by(Task.status, Task.position, Task.id)
    ).all()


@app.post("/api/tasks", response_model=TaskResponse, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(
        title=payload.title.strip(),
        description=payload.description.strip(),
        status=payload.status,
        position=next_position(db, payload.status),
    )

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.patch("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    changes = payload.model_dump(exclude_unset=True)

    if "title" in changes:
        task.title = changes["title"].strip()

    if "description" in changes:
        task.description = changes["description"].strip()

    if "status" in changes:
        new_status = changes["status"]

        if new_status != task.status and "position" not in changes:
            task.position = next_position(db, new_status)

        task.status = new_status

    if "position" in changes:
        task.position = changes["position"]

    db.commit()
    db.refresh(task)
    return task


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
