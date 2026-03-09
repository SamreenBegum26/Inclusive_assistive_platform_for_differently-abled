from pydantic import BaseModel, EmailStr
from enum import Enum


class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: RoleEnum        # ✅ only "admin" or "user" allowed, shows as dropdown in Swagger


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str