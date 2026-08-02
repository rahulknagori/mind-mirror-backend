from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ..core.database import Base


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    purchase_id = Column(UUID(as_uuid=True), ForeignKey("purchases.id"), nullable=False, index=True)
    medicine_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False, index=True)

    medicine_name = Column(String(255), nullable=False)
    batch_number = Column(String(255), nullable=True)
    expiry_date = Column(String(50), nullable=True)

    mrp = Column(Numeric(10, 2), nullable=True)
    purchase_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)

    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    tax_rate = Column(Numeric(5, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    line_total = Column(Numeric(12, 2), nullable=False)

    purchase = relationship("Purchase", back_populates="purchase_items")
    medicine = relationship("Medicine")
