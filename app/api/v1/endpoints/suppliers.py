from .... import schemas
from ....core.database import get_db
from ....models.supplier import Supplier
from ....models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from ....api.deps import get_current_user
from typing import List
from uuid import UUID
router = APIRouter()

@router.post("/", response_model=schemas.supplier.SupplierResponse)
def create_supplier(
    supplier: schemas.supplier.SupplierCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if supplier.credit_days < 0:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Credit days cannot be negative"
        )

    if supplier.opening_balance < 0:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Opening balance cannot be negative"
        )

    if supplier.drug_license_expiry and supplier.drug_license_expiry < date.today():
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Drug license expiry date cannot be in the past"
        )
    try:
        db_supplier= Supplier(
            user_id=current_user.id,
            supplier_name = supplier.supplier_name,
            contact_person = supplier.contact_person,
            phone = supplier.phone,
            email = supplier.email,

            address = supplier.address,
            city = supplier.city,
            state = supplier.state,

            gst_number = supplier.gst_number,
            drug_license_number = supplier.drug_license_number,
            drug_license_expiry = supplier.drug_license_expiry,

            credit_days = supplier.credit_days,
            opening_balance = supplier.opening_balance,
            is_active = supplier.is_active
        )

        db.add(db_supplier)
        db.commit()
        db.refresh(db_supplier)
        return db_supplier
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"Failed to create supplier: {str(e)}"
        )        


@router.get("/", response_model=List[schemas.supplier.SupplierResponse])
def get_supplier(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try: 
         db_suppliers = db.query(Supplier).filter(Supplier.user_id == current_user.id).all()
         return db_suppliers

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suppliers: {str(e)}"        )      

@router.get("/{id}", response_model=schemas.supplier.SupplierResponse)
def get_supplier_by_id(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        db_supplier= db.query(Supplier).filter(
            Supplier.id == id,
            Supplier.user_id == current_user.id).first()
        if not db_supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier with id {supplier_id} not found for user {current_user.id}"   
            )   

        return db_supplier
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get supplier by id: {str(e)}"        )                              