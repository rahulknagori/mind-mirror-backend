from fastapi import APIRouter
from .endpoints import users, medicines, suppliers

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(medicines.router, prefix="/medicines", tags=['Medicines'])
api_router.include_router(suppliers.router, prefix="/supplier", tags=["Supplier"])


