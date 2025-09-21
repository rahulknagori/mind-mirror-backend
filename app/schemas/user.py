from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    firebase_uid: str

class UserCreate(UserBase):
    full_name: Optional[str] = None

class UserOut(UserBase):
    id: int
    full_name: Optional[str]
    class Config:
        orm_mode = True    