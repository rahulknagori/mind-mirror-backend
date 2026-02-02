from fastapi import Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List

from .response import ErrorResponse, ErrorDetail, ErrorCode, create_meta
from ..schemas.response import ErrorInfo


class BaseAPIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[List[ErrorDetail]] = None
    ):
        self.error_code = error_code
        self.details = details or []
        super().__init__(status_code=status_code, detail=message)


class ValidationError(BaseAPIException):
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[List[ErrorDetail]] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details
        )


class NotFoundError(BaseAPIException):
    """Resource not found exception"""
    def __init__(
        self,
        resource: str = "Resource",
        resource_id: Optional[str] = None
    ):
        message = f"{resource} not found"
        if resource_id:
            message += f" with id {resource_id}"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.NOT_FOUND,
            message=message
        )


class UnauthorizedError(BaseAPIException):
    """Unauthorized access exception"""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCode.UNAUTHORIZED,
            message=message
        )


class ForbiddenError(BaseAPIException):
    """Forbidden access exception"""
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=ErrorCode.FORBIDDEN,
            message=message
        )


class ConflictError(BaseAPIException):
    """Conflict exception (e.g., duplicate resource)"""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code=ErrorCode.CONFLICT,
            message=message
        )


class InternalServerError(BaseAPIException):
    """Internal server error exception"""
    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=message
        )


async def api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Handle custom API exceptions"""
    error_info = ErrorInfo(
        code=exc.error_code,
        message=exc.detail,
        details=exc.details if exc.details else None
    )
    error_response = ErrorResponse(
        success=False,
        error=error_info,
        meta=create_meta(request)
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode='json', exclude_none=True)
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions and convert to standard format"""
    # Map HTTP status codes to error codes
    error_code_map = {
        status.HTTP_400_BAD_REQUEST: ErrorCode.BAD_REQUEST,
        status.HTTP_401_UNAUTHORIZED: ErrorCode.UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN: ErrorCode.FORBIDDEN,
        status.HTTP_404_NOT_FOUND: ErrorCode.NOT_FOUND,
        status.HTTP_409_CONFLICT: ErrorCode.CONFLICT,
        status.HTTP_422_UNPROCESSABLE_ENTITY: ErrorCode.VALIDATION_ERROR,
        status.HTTP_500_INTERNAL_SERVER_ERROR: ErrorCode.INTERNAL_SERVER_ERROR,
    }
    
    error_code = error_code_map.get(exc.status_code, ErrorCode.BAD_REQUEST)
    
    error_info = ErrorInfo(
        code=error_code,
        message=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        details=None
    )
    
    error_response = ErrorResponse(
        success=False,
        error=error_info,
        meta=create_meta(request)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode='json', exclude_none=True)
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    error_info = ErrorInfo(
        code=ErrorCode.INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred",
        details=None
    )
    
    error_response = ErrorResponse(
        success=False,
        error=error_info,
        meta=create_meta(request)
    )
    
    # In production, you might want to log the actual exception here
    # logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(mode='json', exclude_none=True)
    )
