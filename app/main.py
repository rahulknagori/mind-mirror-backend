from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4
from .core import database
from .models import user
from .api.v1 import api
from .core.exceptions import (
    BaseAPIException,
    api_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from fastapi.exceptions import HTTPException

user.Base.metadata.create_all(bind=database.engine) 

app = FastAPI(title="Scalable Fast API")

# Request ID Middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        return response

# Add middleware - order matters: RequestIDMiddleware should be first
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Add exception handlers
app.add_exception_handler(BaseAPIException, api_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(api.api_router, prefix='/api/v1')

@app.get("/")
def root():
    return {"message": "API is running"}