from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: UUID
    full_name: Optional[str]
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"    