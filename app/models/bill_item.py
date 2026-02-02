from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ..core.database import Base


class BillItem(Base):
    __tablename__ = "bill_items"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"), nullable=False, index=True)
    medicine_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False, index=True)

    medicine_name = Column(String(255), nullable=False)
    batch_number = Column(String(255), nullable=True)
    expiry_date = Column(String(50), nullable=True)

    mrp = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)   
    quantity = Column(Integer, nullable=False)

    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    tax_rate = Column(Numeric(5, 2), nullable=False, default=0)  # 
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    line_total = Column(Numeric(12, 2), nullable=False)  

    bill = relationship("Bill", back_populates="bill_items")
    medicine = relationship("Medicine")





