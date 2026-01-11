from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List, Any
from datetime import datetime
from uuid import UUID

T = TypeVar('T')

class ErrorDetail(BaseModel):
    """Schema for field-specific error details"""
    field: Optional[str] = None
    message: str

class ErrorInfo(BaseModel):
    """Schema for error information"""
    code: str
    message: str
    details: Optional[List[ErrorDetail]] = None

class MetaInfo(BaseModel):
    """Schema for response metadata"""
    timestamp: datetime
    request_id: Optional[str] = None

class BaseResponse(BaseModel):
    """Base response schema with common fields"""
    success: bool
    message: Optional[str] = None
    meta: MetaInfo

class SuccessResponse(BaseResponse, Generic[T]):
    """Generic success response schema"""
    data: T
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseResponse):
    """Error response schema"""
    error: ErrorInfo
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool

class PaginatedResponse(BaseResponse, Generic[T]):
    """Paginated response schema"""
    data: List[T]
    pagination: PaginationMeta
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
