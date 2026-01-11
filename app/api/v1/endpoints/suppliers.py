from .... import schemas
from ....core.database import get_db
from ....core.response import success_response
from ....core.exceptions import ValidationError, NotFoundError, ErrorDetail
from ....models.supplier import Supplier
from ....models.user import User
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from datetime import date
from ....api.deps import get_current_user
from typing import List
from uuid import UUID
router = APIRouter()

@router.post("/", response_model=schemas.response.SuccessResponse[schemas.supplier.SupplierResponse])
def create_supplier(
    supplier: schemas.supplier.SupplierCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validation checks
    errors = []
    if supplier.credit_days < 0:
        errors.append(ErrorDetail(field="credit_days", message="Credit days cannot be negative"))

    if supplier.opening_balance < 0:
        errors.append(ErrorDetail(field="opening_balance", message="Opening balance cannot be negative"))

    if supplier.drug_license_expiry and supplier.drug_license_expiry < date.today():
        errors.append(ErrorDetail(field="drug_license_expiry", message="Drug license expiry date cannot be in the past"))

    if errors:
        raise ValidationError(message="Validation failed", details=errors)

    try:
        db_supplier = Supplier(
            user_id=current_user.id,
            supplier_name=supplier.supplier_name,
            contact_person=supplier.contact_person,
            phone=supplier.phone,
            email=supplier.email,
            address=supplier.address,
            city=supplier.city,
            state=supplier.state,
            gst_number=supplier.gst_number,
            drug_license_number=supplier.drug_license_number,
            drug_license_expiry=supplier.drug_license_expiry,
            credit_days=supplier.credit_days,
            opening_balance=supplier.opening_balance,
            is_active=supplier.is_active
        )

        db.add(db_supplier)
        db.commit()
        db.refresh(db_supplier)
        
        supplier_response = schemas.supplier.SupplierResponse.model_validate(db_supplier)
        return success_response(
            data=supplier_response,
            message="Supplier created successfully",
            request=request
        )
    except Exception as e:
        raise ValidationError(
            message=f"Failed to create supplier: {str(e)}"
        )        


@router.get("/", response_model=schemas.response.SuccessResponse[List[schemas.supplier.SupplierResponse]])
def get_supplier(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try: 
        db_suppliers = db.query(Supplier).filter(Supplier.user_id == current_user.id).all()
        suppliers_response = [schemas.supplier.SupplierResponse.model_validate(s) for s in db_suppliers]
        return success_response(
            data=suppliers_response,
            message="Suppliers retrieved successfully",
            request=request
        )
    except Exception as e:
        raise ValidationError(
            message=f"Failed to get suppliers: {str(e)}"
        )      

@router.get("/{id}", response_model=schemas.response.SuccessResponse[schemas.supplier.SupplierResponse])
def get_supplier_by_id(
    id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        db_supplier = db.query(Supplier).filter(
            Supplier.id == id,
            Supplier.user_id == current_user.id
        ).first()
        
        if not db_supplier:
            raise NotFoundError(
                resource="Supplier",
                resource_id=str(id)
            )

        supplier_response = schemas.supplier.SupplierResponse.model_validate(db_supplier)
        return success_response(
            data=supplier_response,
            message="Supplier retrieved successfully",
            request=request
        )
    except NotFoundError:
        raise
    except Exception as e:
        raise ValidationError(
            message=f"Failed to get supplier by id: {str(e)}"
        )                              