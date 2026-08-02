from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False, index=True)

    purchase_number = Column(String(50), unique=True, nullable=False, index=True)
    purchase_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    sub_total = Column(Numeric(12, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(12, 2), nullable=False, default=0)
    discount_percentage = Column(Numeric(5, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(12, 2), nullable=False, default=0)
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)

    payment_method = Column(String(20), nullable=False)
    paid_amount = Column(Numeric(12, 2), nullable=False, default=0)
    balance_amount = Column(Numeric(12, 2), nullable=False, default=0)

    status = Column(String(20), nullable=False, default="received")

    notes = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    purchase_items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")
    supplier = relationship("Supplier", back_populates="purchases")
