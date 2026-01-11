from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .... import schemas
from ....api.deps import get_current_user
from ....core.database import get_db
from ....models.medicine import Medicine
from ....models.user import User
from datetime import datetime, date
from typing import List
router = APIRouter()

@router.post("/", response_model=schemas.medicine.MedicineResponse)
def create_medicine(
    medicine: schemas.medicine.MedicineCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if medicine.selling_price > medicine.mrp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selling price cannot be greater than MRP"
        )
    
    if medicine.stock_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock quantity cannot be negative"
        )

    if medicine.expiry_date and medicine.expiry_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expiry date cannot be in the past"
        )


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
        return db_medicine
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create medicine: {str(e)}"
        )    

@router.get("/", response_model=List[schemas.medicine.MedicineResponse]) 
def get_medicines(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
 ):
    try:
        db_medicines = db.query(Medicine).filter(Medicine.user_id==current_user.id).all()
        return db_medicines
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get medicines: {str(e)}"        )       