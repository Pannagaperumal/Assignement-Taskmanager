from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List
import random 
from fastapi import Query

from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi import Path


DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    priority = Column(Integer, default=3)
    owner = Column(String, nullable=False)
    command = Column(String, nullable=False)
    status = Column(String, default="running")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    

Base.metadata.create_all(bind=engine)

class TaskCreate(BaseModel):
    name: str = Field(..., example="Daily backup")
    priority: int = Field(3, ge=0, le=5, example=2, description="Priority from 0 (lowest) to 5 (highest)")
    owner: str = Field(..., example="admin", description="User who initiated the task")
    command: str = Field(..., example="rsync -avz /data /backup", description="Simulated command or operation")

class TaskOut(BaseModel):
    id: int
    name: str
    priority: int
    owner: str
    command: str
    status: str
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


app = FastAPI(
    title="Unix-Inspired Task Manager API",
    description="""
This API simulates Unix-style process/task management.
You can use it to:
- **Create** new tasks (`POST /tasks`)
- **List** all existing tasks (`GET /tasks`)

Think of each task as a 'process' with a name, ID, and status.
""",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc"      # ReDoc UI (optional)
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- API Endpoints ----------
@app.get("/tasks", response_model=List[TaskOut], tags=["Tasks"])
def list_tasks():
    """
    List all existing tasks.

    Returns a list of all tasks stored in the database.
    Each task includes its ID, name, status, and timestamps.
    """
    db = next(get_db())
    return db.query(Task).all()


@app.post("/tasks", response_model=TaskOut, tags=["Tasks"])
def create_task(task: TaskCreate):
    db = next(get_db())

    # Generate a Unix-style process ID (e.g., 1000–99999)
    pid = random.randint(1000, 99999)

    # Ensure the PID is unique in DB
    while db.query(Task).filter(Task.id == pid).first():
        pid = random.randint(1000, 99999)

    new_task = Task(
        id=pid,
        name=task.name,
        priority=task.priority,
        owner=task.owner,
        command=task.command
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get("/tasks", response_model=List[TaskOut], tags=["Tasks"])
def list_tasks(status: str = Query(None, description="Filter tasks by status (e.g., running, completed)"), db: Session = Depends(get_db)):
    """
    List all tasks or filter by status.
    Use `?status=running` or `?status=completed` to filter.
    """
    if status:
        return db.query(Task).filter(Task.status == status).all()
    return db.query(Task).all()


@app.patch("/tasks/{task_id}", response_model=TaskOut, tags=["Tasks"])
def complete_task(task_id: int = Path(..., description="Process ID of the task to complete"), db: Session = Depends(get_db)):
    """
    Simulate task completion by updating its status to 'completed' and timestamp.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "completed"
    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)
    return task