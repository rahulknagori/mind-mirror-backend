from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel
from .purchase_item import PurchaseItemCreate


class PurchaseBase(BaseModel):
    supplier_id: UUID
    purchase_number: str
    purchase_date: datetime
    sub_total: Decimal
    discount_amount: Decimal
    discount_percentage: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    payment_method: str
    paid_amount: Decimal
    balance_amount: Decimal
    status: Optional[str] = "received"
    notes: Optional[str] = None


class PurchaseCreate(BaseModel):
    """Schema for creating a purchase. Totals are calculated by backend."""
    supplier_id: UUID
    purchase_number: str
    purchase_date: datetime
    payment_method: str
    paid_amount: Decimal
    balance_amount: Decimal
    status: Optional[str] = "received"
    notes: Optional[str] = None
    purchase_items: List[PurchaseItemCreate]  # Nested purchase items
    # sub_total, discount_amount, discount_percentage, tax_amount, total_amount are calculated by backend


class PurchaseUpdate(BaseModel):
    """Limited update: business fields only. Items and totals are immutable after creation."""
    payment_method: Optional[str] = None
    paid_amount: Optional[Decimal] = None
    balance_amount: Optional[Decimal] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class PurchaseResponse(PurchaseBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
