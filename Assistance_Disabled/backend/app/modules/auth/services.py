from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, create_access_token
from app.modules.auth import repository


def register_user(db: Session, email: str, password: str, role: str):
    existing_user = repository.get_user_by_email(db, email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(password)
    return repository.create_user(db, email, hashed_pw, role)


def login_user(db: Session, email: str, password: str):
    user = repository.get_user_by_email(db, email)

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )

    return token
