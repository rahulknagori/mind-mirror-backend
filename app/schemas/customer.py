from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class CustomerBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    credit_limit: Decimal = 0
    outstanding_balance: Decimal = 0
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
