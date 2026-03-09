from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.users.models import User
from app.modules.auth.dependencies import get_current_admin

router = APIRouter()

# 👥 Get all users (ADMIN ONLY)
@router.get("/")
def get_all_users(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ]
