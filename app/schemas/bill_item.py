from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from decimal import Decimal


class BillItemBase(BaseModel):
    medicine_id: UUID
    medicine_name: str
    batch_number: Optional[str] = None
    expiry_date: Optional[str] = None
    mrp: Decimal
    selling_price: Decimal
    quantity: int
    discount_amount: Decimal = 0
    tax_rate: Decimal = 0
    tax_amount: Decimal = 0
    line_total: Decimal


class BillItemCreate(BaseModel):
    """Schema for creating a bill item. tax_amount and line_total are calculated by backend."""
    medicine_id: UUID
    medicine_name: str
    batch_number: Optional[str] = None
    expiry_date: Optional[str] = None
    mrp: Decimal
    selling_price: Decimal
    quantity: int
    discount_amount: Decimal = 0
    tax_rate: Decimal = 0
    # tax_amount and line_total are calculated by backend, not sent from frontend


class BillItemResponse(BillItemBase):
    id: UUID
    bill_id: UUID
    
    class Config:
        from_attributes = True
