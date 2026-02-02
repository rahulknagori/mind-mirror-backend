from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from ..models.customer import Customer
from ..models.user import User
from ..core.exceptions import NotFoundError


class CustomerService:
    
    @staticmethod
    async def validate_customer_exists(
        db: AsyncSession,
        customer_id: UUID,
        user_id: UUID
    ) -> Customer:
        result = await db.execute(
            select(Customer).where(
                Customer.id == customer_id,
                Customer.user_id == user_id
            )
        )
        customer = result.scalar_one_or_none()
        
        if not customer:
            raise NotFoundError(
                resource="Customer",
                resource_id=str(customer_id)
            )
        
        return customer
