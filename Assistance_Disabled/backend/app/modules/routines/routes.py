from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import List

from app.modules.users.models import User
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.routines.models import RoutineTask, TaskCompletion
from app.modules.routines.schemas import TaskCreate, TaskResponse, ProgressResponse

router = APIRouter()


# ====================================
# CREATE / ASSIGN TASK (ADMIN ONLY)
# ====================================
@router.post("/create", response_model=TaskResponse)
def create_task(
    payload: TaskCreate,                           # ✅ use schema properly
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only admin can assign tasks
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can assign tasks")

    # ✅ ROOT CAUSE FIX: Check user exists AND belongs to this admin
    user = db.query(User).filter(
        User.id == payload.user_id,
        User.admin_id == current_user.id           # ✅ this now works because admin_id is set at registration
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found or not assigned to you. Make sure the user was registered under your admin account."
        )

    new_task = RoutineTask(
        title=payload.title,
        category=payload.category,
        scheduled_time=payload.scheduled_time,
        assigned_to=payload.user_id,
        assigned_by=current_user.id,               # ✅ track which admin assigned
        completed=False
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


# ====================================
# GET ALL TASKS FOR A USER (ADMIN)
# ====================================
@router.get("/user/{user_id}", response_model=List[TaskResponse])
def get_user_tasks(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Admin can see their users' tasks
    if current_user.role == "admin":
        # Verify user belongs to this admin
        user = db.query(User).filter(
            User.id == user_id,
            User.admin_id == current_user.id
        ).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found or not under your account")

    # User can only see their own tasks
    elif current_user.role == "user":
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only view your own tasks")
    
    tasks = db.query(RoutineTask).filter(
        RoutineTask.assigned_to == user_id
    ).all()

    return tasks


# ====================================
# GET MY TASKS (USER)
# ====================================
@router.get("/my-tasks", response_model=List[TaskResponse])
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Admins don't have tasks. Use /user/{user_id} instead.")

    tasks = db.query(RoutineTask).filter(
        RoutineTask.assigned_to == current_user.id
    ).all()

    return tasks


# ====================================
# COMPLETE TASK (USER ONLY)
# ====================================
@router.post("/complete/{task_id}")
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Admin cannot complete tasks
    if current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Admins cannot complete tasks")

    task = db.query(RoutineTask).filter(RoutineTask.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # ✅ Only the assigned user can complete their own task
    if task.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="You can only complete tasks assigned to you")

    # Prevent completing twice
    if task.completed:
        raise HTTPException(status_code=400, detail="Task already completed")

    # Mark as done
    task.completed = True

    completion_entry = TaskCompletion(
        task_id=task.id,
        status="completed"
    )

    db.add(completion_entry)
    db.commit()

    return {"message": "Task completed successfully! 🎉"}


# ====================================
# DAILY PROGRESS (USER)
# ====================================
@router.get("/daily-progress", response_model=ProgressResponse)
def daily_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Use /admin-progress/{user_id} to see a user's progress")

    today = date.today()

    total_tasks = db.query(RoutineTask).filter(
        RoutineTask.assigned_to == current_user.id
    ).count()

    completed_today = db.query(TaskCompletion).join(
        RoutineTask, TaskCompletion.task_id == RoutineTask.id
    ).filter(
        RoutineTask.assigned_to == current_user.id,
        func.date(TaskCompletion.completed_at) == today
    ).count()

    if total_tasks == 0:
        return ProgressResponse(total_tasks=0, completed_today=0, progress_percentage=0.0)

    return ProgressResponse(
        total_tasks=total_tasks,
        completed_today=completed_today,
        progress_percentage=round((completed_today / total_tasks) * 100, 2)
    )


# ====================================
# ADMIN: SEE ANY USER'S PROGRESS
# ====================================
@router.get("/admin-progress/{user_id}", response_model=ProgressResponse)
def admin_view_progress(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    # Verify user belongs to this admin
    user = db.query(User).filter(
        User.id == user_id,
        User.admin_id == current_user.id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found or not under your account")

    today = date.today()

    total_tasks = db.query(RoutineTask).filter(
        RoutineTask.assigned_to == user_id
    ).count()

    completed_today = db.query(TaskCompletion).join(
        RoutineTask, TaskCompletion.task_id == RoutineTask.id
    ).filter(
        RoutineTask.assigned_to == user_id,
        func.date(TaskCompletion.completed_at) == today
    ).count()

    if total_tasks == 0:
        return ProgressResponse(total_tasks=0, completed_today=0, progress_percentage=0.0)

    return ProgressResponse(
        total_tasks=total_tasks,
        completed_today=completed_today,
        progress_percentage=round((completed_today / total_tasks) * 100, 2)
    )