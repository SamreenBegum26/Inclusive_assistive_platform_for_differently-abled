from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    title: str
    category: str
    scheduled_time: str    # ✅ matches model (String, e.g. "08:00 AM")
    user_id: int           # ✅ which user to assign to


class TaskResponse(BaseModel):
    id: int
    title: str
    category: str
    scheduled_time: str
    assigned_to: int
    assigned_by: int
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProgressResponse(BaseModel):
    total_tasks: int
    completed_today: int
    progress_percentage: float