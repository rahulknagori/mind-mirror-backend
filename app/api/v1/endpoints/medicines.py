from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from .... import schemas
from ....api.deps import get_current_user
from ....core.database import get_db
from ....core.response import success_response
from ....core.exceptions import ValidationError, ErrorDetail
from ....models.medicine import Medicine
from ....models.user import User
from datetime import datetime, date
from typing import List
router = APIRouter()

@router.post("/", response_model=schemas.response.SuccessResponse[schemas.medicine.MedicineResponse])
def create_medicine(
    medicine: schemas.medicine.MedicineCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
    except Exception as e:
        raise ValidationError(
            message=f"Failed to create medicine: {str(e)}"
        )    

@router.get("/", response_model=schemas.response.SuccessResponse[List[schemas.medicine.MedicineResponse]]) 
def get_medicines(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
 ):
    try:
        db_medicines = db.query(Medicine).filter(Medicine.user_id==current_user.id).all()
        medicines_response = [schemas.medicine.MedicineResponse.model_validate(m) for m in db_medicines]
        return success_response(
            data=medicines_response,
            message="Medicines retrieved successfully",
            request=request
        )
    except Exception as e:
        raise ValidationError(
            message=f"Failed to get medicines: {str(e)}"
        )       