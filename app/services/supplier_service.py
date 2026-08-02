from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from ..models.supplier import Supplier
from ..core.exceptions import NotFoundError


class SupplierService:

    @staticmethod
    async def validate_supplier_exists(
        db: AsyncSession,
        supplier_id: UUID,
        user_id: UUID
    ) -> Supplier:
        result = await db.execute(
            select(Supplier).where(
                Supplier.id == supplier_id,
                Supplier.user_id == user_id
            )
        )
        supplier = result.scalar_one_or_none()

        if not supplier:
            raise NotFoundError(
                resource="Supplier",
                resource_id=str(supplier_id)
            )

        return supplier
