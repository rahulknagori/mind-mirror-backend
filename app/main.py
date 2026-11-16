from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4
from .core import database
from .core.config import settings
from .core.auth_cookies import CSRF_HEADER_NAME
from .core.csrf import CSRFMiddleware
from .models import user  # Keep for backward compatibility if needed
# Import all models to ensure SQLAlchemy can resolve relationships
from .models import User, Medicine, Supplier, Customer, Bill, BillItem
from .api.v1 import api
from .core.exceptions import (
    BaseAPIException,
    api_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from fastapi.exceptions import HTTPException

# Note: For async, table creation should be done via Alembic migrations
# This line is kept for backward compatibility but won't work with async engine
# Remove this line and use migrations instead: alembic upgrade head 

app = FastAPI(title="Scalable Fast API")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        return response

# Middleware: the last one added runs first. CORS must be outermost so that even
# error responses (e.g. CSRF rejections) carry CORS headers.
app.add_middleware(CSRFMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    # Cookies are sent cross-origin, so only our own frontend(s) may be allowed.
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", CSRF_HEADER_NAME],
)

app.add_exception_handler(BaseAPIException, api_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(api.api_router, prefix='/api/v1')

@app.get("/")
async def root():
    return {"message": "API is running"}