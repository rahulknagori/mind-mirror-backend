from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..core.database import Base

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True) 
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    brand_name = Column(String(255))
    composition = Column(String(255))
    batch_number = Column(String(255))
    expiry_date = Column(Date)
    mrp = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)  # Stock Quantity
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
