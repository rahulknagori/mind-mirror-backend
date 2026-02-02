# app/models/customer.py
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime
import uuid
from ..core.database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True, index=True)
    email = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    
    credit_limit = Column(Numeric(12, 2), nullable=False, default=0)
    outstanding_balance = Column(Numeric(12, 2), nullable=False, default=0)
    
    is_active = Column(Boolean, nullable=False, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    bills = relationship("Bill", back_populates="customer")