from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel
from .bill_item import BillItemCreate


class BillBase(BaseModel):
    customer_id: Optional[UUID] = None
    bill_number: str
    bill_date: datetime
    sub_total: Decimal
    discount_amount: Decimal
    discount_percentage: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    payment_method: str
    paid_amount: Decimal
    balance_amount: Decimal
    status: Optional[str] = "completed"
    notes: Optional[str] = None
    docter_name: Optional[str] = None

class BillCreate(BaseModel):
    """Schema for creating a bill. Totals are calculated by backend."""
    customer_id: Optional[UUID] = None
    bill_number: str
    bill_date: datetime
    payment_method: str
    paid_amount: Decimal
    balance_amount: Decimal
    status: Optional[str] = "completed"
    notes: Optional[str] = None
    docter_name: Optional[str] = None
    bill_items: List[BillItemCreate]  # Nested bill items
    # sub_total, discount_amount, discount_percentage, tax_amount, total_amount are calculated by backend

class BillUpdate(BaseModel):
    """Limited update: business fields only. Items and totals are immutable after creation."""
    payment_method: Optional[str] = None
    paid_amount: Optional[Decimal] = None
    balance_amount: Optional[Decimal] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    docter_name: Optional[str] = None

class BillResponse(BillBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True