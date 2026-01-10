from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

class SupplierBase(BaseModel):
    supplier_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    gst_number: Optional[str] = None
    drug_license_number: Optional[str] = None
    drug_license_expiry: Optional[date] = None
    credit_days: int = 15
    opening_balance: Decimal = 0
    is_active: bool = True

class SupplierCreate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True