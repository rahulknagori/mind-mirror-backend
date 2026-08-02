from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

class MedicineBase(BaseModel):
    name: str
    type: str
    brand_name: Optional[str] = None
    composition: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    mrp: Decimal
    selling_price: Decimal
    stock_quantity: int = 0

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    brand_name: Optional[str] = None
    composition: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    mrp: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None

class MedicineResponse(MedicineBase):
    id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  