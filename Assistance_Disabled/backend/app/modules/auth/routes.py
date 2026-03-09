from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import get_db
from app.modules.users.models import User
from app.modules.auth.dependencies import get_current_user, get_current_admin
from app.modules.auth.schemas import UserRegister
from app.modules.auth.utils import (
    create_access_token,
    get_password_hash,
    verify_password
)

router = APIRouter()

# auth/routes.py - replace your register endpoint with these two:

# 1️⃣ REGISTER ADMIN (no admin_id needed)
@router.post("/register/admin")
def register_admin(
    payload: UserRegister,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role="admin",
        admin_id=None  # ✅ admin has no admin_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Admin registered successfully", "admin_id": new_user.id}


# 2️⃣ REGISTER DISABLED USER (must link to an admin)
@router.post("/register/user")
def register_user(
    payload: UserRegister,
    admin_id: int,             # ✅ required for users
    db: Session = Depends(get_db)
):
    # Check email not taken
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    # ✅ Verify the admin actually exists
    admin = db.query(User).filter(
        User.id == admin_id,
        User.role == "admin"
    ).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found. Register the admin first!")

    new_user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role="user",
        admin_id=admin_id      # ✅ linked to admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}


# 🔐 LOGIN
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )

    if not verify_password(form_data.password, user.hashed_password):  # ✅ correct field
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )

    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# 👤 GET CURRENT USER
@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "admin_id": current_user.admin_id
    }


# 🔒 ADMIN ONLY ROUTE
@router.get("/admin-only")
def admin_route(current_admin: User = Depends(get_current_admin)):
    return {"message": "Welcome Admin!"}