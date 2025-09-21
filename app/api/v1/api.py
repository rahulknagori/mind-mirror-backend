from fastapi import APIRouter
from .endpoints import users, journal

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(journal.router, prefix="/journal", tags=["Journal"])
