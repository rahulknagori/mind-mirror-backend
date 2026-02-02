from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from ..models.medicine import Medicine
from ..core.exceptions import NotFoundError


class MedicineService:
    
    @staticmethod
    async def validate_medicine_exists(
        db: AsyncSession,
        medicine_id: UUID,
        user_id: UUID
    ) -> Medicine:
        result = await db.execute(
            select(Medicine).where(
                Medicine.id == medicine_id,
                Medicine.user_id == user_id
            )
        )
        medicine = result.scalar_one_or_none()
        
        if not medicine:
            raise NotFoundError(
                resource="Medicine",
                resource_id=str(medicine_id)
            )
        
        return medicine
