from typing import Optional, List, TypeVar, Any
from datetime import datetime
from fastapi import Request
from uuid import uuid4

from ..schemas.response import (
    SuccessResponse,
    ErrorResponse,
    ErrorInfo,
    ErrorDetail,
    MetaInfo,
    PaginatedResponse,
    PaginationMeta
)

T = TypeVar('T')

# Standard Error Codes
class ErrorCode:
    """Standard error codes for API responses"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    BAD_REQUEST = "BAD_REQUEST"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    CONFLICT = "CONFLICT"
    UNPROCESSABLE_ENTITY = "UNPROCESSABLE_ENTITY"


def get_request_id(request: Request) -> Optional[str]:
    """Extract request ID from request state"""
    return getattr(request.state, "request_id", None)


def create_meta(request: Optional[Request] = None) -> MetaInfo:
    """Create metadata for response"""
    request_id = get_request_id(request) if request else None
    return MetaInfo(
        timestamp=datetime.utcnow(),
        request_id=request_id
    )


def success_response(
    data: T,
    message: Optional[str] = "Operation completed successfully",
    request: Optional[Request] = None
) -> SuccessResponse[T]:
    """Create a success response"""
    return SuccessResponse(
        success=True,
        message=message,
        data=data,
        meta=create_meta(request)
    )


def error_response(
    code: str,
    message: str,
    details: Optional[List[ErrorDetail]] = None,
    request: Optional[Request] = None
) -> ErrorResponse:
    """Create an error response"""
    error_info = ErrorInfo(
        code=code,
        message=message,
        details=details
    )
    return ErrorResponse(
        success=False,
        error=error_info,
        meta=create_meta(request)
    )


def paginated_response(
    data: List[T],
    page: int,
    page_size: int,
    total_items: int,
    message: Optional[str] = "Data retrieved successfully",
    request: Optional[Request] = None
) -> PaginatedResponse[T]:
    """Create a paginated response"""
    total_pages = (total_items + page_size - 1) // page_size if page_size > 0 else 0
    
    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )
    
    return PaginatedResponse(
        success=True,
        message=message,
        data=data,
        pagination=pagination,
        meta=create_meta(request)
    )
