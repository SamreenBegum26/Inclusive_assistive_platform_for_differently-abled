from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class RoutineTask(Base):
    __tablename__ = "routine_tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    scheduled_time = Column(String, nullable=False)   # e.g. "08:00 AM"

    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)  # ✅ which user
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # ✅ which admin assigned it

    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[assigned_to])
    admin = relationship("User", foreign_keys=[assigned_by])
    completions = relationship("TaskCompletion", back_populates="task")


class TaskCompletion(Base):
    __tablename__ = "task_completions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("routine_tasks.id"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")

    # Relationship back to task
    task = relationship("RoutineTask", back_populates="completions")