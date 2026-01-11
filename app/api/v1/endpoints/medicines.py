from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError as PydanticValidationError
from .... import schemas
from ....api.deps import get_current_user
from ....core.database import get_db
from ....core.response import success_response
from ....core.exceptions import ValidationError, InternalServerError, ErrorDetail
from ....models.medicine import Medicine
from ....models.user import User
from datetime import datetime, date
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/")
def create_medicine(
    medicine: schemas.medicine.MedicineCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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
        db.commit()
        db.refresh(db_medicine)
        
        medicine_response = schemas.medicine.MedicineResponse.model_validate(db_medicine)
        return success_response(
            data=medicine_response,
            message="Medicine created successfully",
            request=request
        )
    except SQLAlchemyError as e:
        # Database-related errors
        db.rollback()
        logger.error(f"Database error while creating medicine: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to create medicine due to a database error"
        )
    except Exception as e:
        # Unexpected errors
        db.rollback()
        logger.error(f"Unexpected error while creating medicine: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while creating medicine"
        )    

@router.get("/")
def get_medicines(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all medicines for the current user.
    Returns a standardized success response with the list of medicines.
    """
    try:
        db_medicines = db.query(Medicine).filter(Medicine.user_id == current_user.id).all()
        
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
        
        return success_response(
            data=medicines_response,
            message="Medicines retrieved successfully",
            request=request
        )
    except SQLAlchemyError as e:
        db.rollback()
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