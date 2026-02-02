from .... import schemas
from ....core.database import get_db
from ....core.response import success_response
from ....core.exceptions import ValidationError, NotFoundError, ErrorDetail
from ....models.customer import Customer
from ....models.user import User
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ....api.deps import get_current_user
from typing import List
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=schemas.response.SuccessResponse[schemas.customer.CustomerResponse])
async def create_customer(
    customer: schemas.customer.CustomerCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Validation checks
    errors = []
    if customer.credit_limit < 0:
        errors.append(ErrorDetail(field="credit_limit", message="Credit limit cannot be negative"))
    
    if customer.outstanding_balance < 0:
        errors.append(ErrorDetail(field="outstanding_balance", message="Outstanding balance cannot be negative"))
    
    if customer.age is not None and customer.age < 0:
        errors.append(ErrorDetail(field="age", message="Age cannot be negative"))
    
    if customer.gender is not None and customer.gender not in ["male", "female", "other"]:
        errors.append(ErrorDetail(field="gender", message="Gender must be one of: male, female, other"))

    if errors:
        raise ValidationError(message="Validation failed", details=errors)

    try:
        db_customer = Customer(
            user_id=current_user.id,
            name=customer.name,
            phone=customer.phone,
            email=customer.email,
            address=customer.address,
            age=customer.age,
            gender=customer.gender,
            credit_limit=customer.credit_limit,
            outstanding_balance=customer.outstanding_balance,
            is_active=customer.is_active
        )

        db.add(db_customer)
        await db.commit()
        await db.refresh(db_customer)
        
        customer_response = schemas.customer.CustomerResponse.model_validate(db_customer)
        return success_response(
            data=customer_response,
            message="Customer created successfully",
            request=request
        )
    except Exception as e:
        await db.rollback()
        raise ValidationError(
            message=f"Failed to create customer: {str(e)}"
        )        


@router.get("/", response_model=schemas.response.SuccessResponse[List[schemas.customer.CustomerResponse]])
async def get_customers(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try: 
        result = await db.execute(
            select(Customer).where(Customer.user_id == current_user.id)
        )
        db_customers = result.scalars().all()
        customers_response = [schemas.customer.CustomerResponse.model_validate(c) for c in db_customers]
        return success_response(
            data=customers_response,
            message="Customers retrieved successfully",
            request=request
        )
    except Exception as e:
        raise ValidationError(
            message=f"Failed to get customers: {str(e)}"
        )      

@router.get("/{id}", response_model=schemas.response.SuccessResponse[schemas.customer.CustomerResponse])
async def get_customer_by_id(
    id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(Customer).where(
                Customer.id == id,
                Customer.user_id == current_user.id
            )
        )
        db_customer = result.scalar_one_or_none()
        
        if not db_customer:
            raise NotFoundError(
                resource="Customer",
                resource_id=str(id)
            )

        customer_response = schemas.customer.CustomerResponse.model_validate(db_customer)
        return success_response(
            data=customer_response,
            message="Customer retrieved successfully",
            request=request
        )
    except NotFoundError:
        raise
    except Exception as e:
        raise ValidationError(
            message=f"Failed to get customer by id: {str(e)}"
        )
