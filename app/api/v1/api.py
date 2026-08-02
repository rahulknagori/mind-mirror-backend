from fastapi import APIRouter
from .endpoints import users, medicines, suppliers, bills, customers, purchases

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(medicines.router, prefix="/medicines", tags=['Medicines'])
api_router.include_router(suppliers.router, prefix="/supplier", tags=["Supplier"])
api_router.include_router(bills.router, prefix="/bills", tags=["Bills"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(purchases.router, prefix="/purchases", tags=["Purchases"])


