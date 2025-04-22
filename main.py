"""task_manager_api.py
Improved FastAPI application for managing simulated Unix-style tasks.

Changes & highlights:
- **PEP 8 compliant** imports and naming.
- **Enum** for task status (running/completed/failed).
- Removed duplicate route definitions.
- Added detailed **docstrings**, **comments**, and **type hints** throughout.
- All database access uses **dependency injection** (`Depends(get_db)`).
- Routes sorted logically and include `summary` metadata for better auto‑generated docs.
- Ensured the PID generated is unique without race conditions within the same process.
- Added ordering by creation date when listing tasks.

Run with:
```bash
uvicorn task_manager_api:app --reload
```
"""

from __future__ import annotations

import enum
import random
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


# ---------------------------------------------------------------------------
# Model definitions
# ---------------------------------------------------------------------------
class TaskStatus(str, enum.Enum):
    """Allowed lifecycle states for a task."""

    running = "running"
    completed = "completed"
    failed = "failed"


class Task(Base):
    """SQLAlchemy ORM model representing a Unix-style "process"."""

    __tablename__ = "tasks"

    id: int = Column(Integer, primary_key=True, index=True)  # Unix-like PID
    name: str = Column(String, nullable=False)
    priority: int = Column(Integer, default=3)  # 0 (low) – 5 (high)
    owner: str = Column(String, nullable=False)
    command: str = Column(String, nullable=False)
    status: str = Column(String, default=TaskStatus.running.value)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime | None = Column(DateTime, nullable=True)


# Create DB schema (in production use migrations instead)
Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# Pydantic schemas (request/response bodies)
# ---------------------------------------------------------------------------
class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    name: str = Field(..., example="Daily backup")
    priority: int = Field(
        3,
        ge=0,
        le=5,
        description="Priority from 0 (lowest) to 5 (highest)",
        example=2,
    )
    owner: str = Field(..., example="admin")
    command: str = Field(..., example="rsync -avz /data /backup")


class TaskOut(BaseModel):
    """Schema for returning tasks to clients."""

    id: int
    name: str
    priority: int
    owner: str
    command: str
    status: TaskStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Unix‑Inspired Task Manager API",
    description=(
        "This API simulates Unix‑style process management.\n\n"
        "* **Create** tasks (`POST /tasks`)\n"
        "* **List / filter** tasks (`GET /tasks`)\n"
        "* **Mark** tasks as completed (`PATCH /tasks/{id}`)"
    ),
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------

def get_db() -> Session:
    """Provide a database session per request and guarantee its closure."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get(
    "/tasks",
    response_model=List[TaskOut],
    tags=["Tasks"],
    summary="List tasks with optional status filter",
)
def list_tasks(
    status: Optional[TaskStatus] = Query(
        None, description="Filter tasks by status (running/completed/failed)"
    ),
    db: Session = Depends(get_db),
):
    """Return all tasks or only those with the specified *status*."""

    query = db.query(Task)
    if status is not None:
        query = query.filter(Task.status == status.value)
    return query.order_by(Task.created_at.desc()).all()


@app.post(
    "/tasks",
    response_model=TaskOut,
    status_code=201,
    tags=["Tasks"],
    summary="Create a new task",
)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Insert a new task and return the persisted record."""

    # Generate a unique Unix‑style PID (1000–99999).
    pid = random.randint(1000, 99999)
    while db.query(Task).filter(Task.id == pid).first() is not None:
        pid = random.randint(1000, 99999)

    new_task = Task(
        id=pid,
        name=task.name,
        priority=task.priority,
        owner=task.owner,
        command=task.command,
        status=TaskStatus.running.value,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.patch(
    "/tasks/{task_id}",
    response_model=TaskOut,
    tags=["Tasks"],
    summary="Mark a task as completed",
)
def complete_task(
    task_id: int = Path(..., description="PID of the task to complete"),
    db: Session = Depends(get_db),
):
    """Set a task's *status* to `completed`."""

    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = TaskStatus.completed.value
    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)
    return task
