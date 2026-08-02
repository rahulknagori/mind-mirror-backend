from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, or_, select
from pydantic import ValidationError as PydanticValidationError
from .... import schemas
from ....api.deps import get_current_user
from ....core.database import get_db
from ....core.response import paginated_response, success_response
from ....core.exceptions import ValidationError, InternalServerError, NotFoundError, ErrorDetail
from ....models.medicine import Medicine
from ....models.user import User
from datetime import datetime, date
from typing import List, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/")
async def create_medicine(
    medicine: schemas.medicine.MedicineCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new medicine for the current user.
    Returns a standardized success response with the created medicine.
    """
    # Validation checks
    errors = []
    if medicine.selling_price > medicine.mrp:
        errors.append(ErrorDetail(field="selling_price", message="Selling price cannot be greater than MRP"))
    
    if medicine.stock_quantity < 0:
        errors.append(ErrorDetail(field="stock_quantity", message="Stock quantity cannot be negative"))

    if medicine.expiry_date and medicine.expiry_date < date.today():
        errors.append(ErrorDetail(field="expiry_date", message="Expiry date cannot be in the past"))

    if errors:
        raise ValidationError(message="Validation failed", details=errors)

    try:
        db_medicine = Medicine(
            user_id=current_user.id,
            name=medicine.name,
            type=medicine.type,
            brand_name=medicine.brand_name,
            composition=medicine.composition,
            batch_number=medicine.batch_number,
            expiry_date=medicine.expiry_date,
            mrp=medicine.mrp,
            selling_price=medicine.selling_price,
            stock_quantity=medicine.stock_quantity
        )

        db.add(db_medicine)
        await db.commit()
        await db.refresh(db_medicine)
        
        medicine_response = schemas.medicine.MedicineResponse.model_validate(db_medicine)
        return success_response(
            data=medicine_response,
            message="Medicine created successfully",
            request=request
        )
    except SQLAlchemyError as e:
        # Database-related errors
        await db.rollback()
        logger.error(f"Database error while creating medicine: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to create medicine due to a database error"
        )
    except Exception as e:
        # Unexpected errors
        await db.rollback()
        logger.error(f"Unexpected error while creating medicine: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while creating medicine"
        )    

@router.get("/")
async def get_medicines(
    request: Request,
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get medicines for the current user, with optional search and pagination.
    Returns a standardized paginated response with the list of medicines.
    """
    try:
        conditions = [Medicine.user_id == current_user.id]
        if search:
            like = f"%{search}%"
            conditions.append(or_(
                Medicine.name.ilike(like),
                Medicine.brand_name.ilike(like),
                Medicine.composition.ilike(like),
                Medicine.batch_number.ilike(like),
            ))

        count_result = await db.execute(select(func.count()).select_from(Medicine).where(*conditions))
        total_items = count_result.scalar_one()

        result = await db.execute(
            select(Medicine)
            .where(*conditions)
            .order_by(Medicine.name.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        db_medicines = result.scalars().all()

        try:
            medicines_response = [
                schemas.medicine.MedicineResponse.model_validate(m)
                for m in db_medicines
            ]
        except PydanticValidationError as e:
            logger.error(f"Validation error while converting medicines to response: {str(e)}", exc_info=True)
            raise InternalServerError(
                message="Failed to process medicine data"
            )

        return paginated_response(
            data=medicines_response,
            page=page,
            page_size=page_size,
            total_items=total_items,
            message="Medicines retrieved successfully",
            request=request
        )
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while fetching medicines: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to retrieve medicines due to a database error"
        )
    except InternalServerError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching medicines: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while retrieving medicines"
        )


@router.get("/{id}")
async def get_medicine(
    id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single medicine by id for the current user.
    """
    try:
        result = await db.execute(
            select(Medicine).where(Medicine.id == id, Medicine.user_id == current_user.id)
        )
        db_medicine = result.scalar_one_or_none()
        if not db_medicine:
            raise NotFoundError(resource="Medicine", resource_id=str(id))

        medicine_response = schemas.medicine.MedicineResponse.model_validate(db_medicine)
        return success_response(
            data=medicine_response,
            message="Medicine retrieved successfully",
            request=request
        )
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching medicine: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to retrieve medicine due to a database error"
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching medicine: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while retrieving medicine"
        )


@router.put("/{id}")
async def update_medicine(
    id: UUID,
    medicine_update: schemas.medicine.MedicineUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a medicine for the current user. Applies the same validation rules as create.
    """
    try:
        result = await db.execute(
            select(Medicine).where(Medicine.id == id, Medicine.user_id == current_user.id)
        )
        db_medicine = result.scalar_one_or_none()
        if not db_medicine:
            raise NotFoundError(resource="Medicine", resource_id=str(id))

        update_data = medicine_update.model_dump(exclude_unset=True)

        merged_selling_price = update_data.get("selling_price", db_medicine.selling_price)
        merged_mrp = update_data.get("mrp", db_medicine.mrp)
        merged_stock_quantity = update_data.get("stock_quantity", db_medicine.stock_quantity)
        merged_expiry_date = update_data.get("expiry_date", db_medicine.expiry_date)

        errors = []
        if merged_selling_price > merged_mrp:
            errors.append(ErrorDetail(field="selling_price", message="Selling price cannot be greater than MRP"))

        if merged_stock_quantity < 0:
            errors.append(ErrorDetail(field="stock_quantity", message="Stock quantity cannot be negative"))

        if merged_expiry_date and merged_expiry_date < date.today():
            errors.append(ErrorDetail(field="expiry_date", message="Expiry date cannot be in the past"))

        if errors:
            raise ValidationError(message="Validation failed", details=errors)

        for field, value in update_data.items():
            setattr(db_medicine, field, value)

        await db.commit()
        await db.refresh(db_medicine)

        medicine_response = schemas.medicine.MedicineResponse.model_validate(db_medicine)
        return success_response(
            data=medicine_response,
            message="Medicine updated successfully",
            request=request
        )
    except (NotFoundError, ValidationError):
        await db.rollback()
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while updating medicine: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to update medicine due to a database error"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error while updating medicine: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while updating medicine"
        )


@router.delete("/{id}")
async def delete_medicine(
    id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a medicine for the current user.
    """
    try:
        result = await db.execute(
            select(Medicine).where(Medicine.id == id, Medicine.user_id == current_user.id)
        )
        db_medicine = result.scalar_one_or_none()
        if not db_medicine:
            raise NotFoundError(resource="Medicine", resource_id=str(id))

        await db.delete(db_medicine)
        await db.commit()

        return success_response(
            data=None,
            message="Medicine deleted successfully",
            request=request
        )
    except NotFoundError:
        await db.rollback()
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while deleting medicine: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to delete medicine due to a database error"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error while deleting medicine: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while deleting medicine"
        )