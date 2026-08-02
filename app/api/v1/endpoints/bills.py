

import logging
from typing import Optional
from sqlalchemy import func, or_, select
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.api.deps import get_current_user
from pydantic import ValidationError as PydanticValidationError
from app.core.database import get_db
from app.core.enums import BillStatus
from app.core.exceptions import ErrorDetail, InternalServerError, NotFoundError, ValidationError
from app.core.response import paginated_response, success_response
from app.models.bill import Bill
from app.models.bill_item import BillItem
from app.models.user import User
from app.services.bill_service import BillService
from app.services.customer_service import CustomerService
from app.services.medicine_service import MedicineService

logger = logging.getLogger(__name__)
router = APIRouter();

@router.post("/")
async def createBill(
    bill: schemas.bill.BillCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    try:
        # Validate customer_id if provided
        if bill.customer_id:
            await CustomerService.validate_customer_exists(
                db=db,
                customer_id=bill.customer_id,
                user_id=current_user.id
            )
        
        for item in bill.bill_items:
            await MedicineService.validate_medicine_exists(
                db=db,
                medicine_id=item.medicine_id,
                user_id=current_user.id
            )
        
        item_totals_list, bill_totals = BillService.calculate_all_totals(bill)
        
        bill_items = [
            BillItem(
                medicine_id=item.medicine_id,
                medicine_name=item.medicine_name,
                batch_number=item.batch_number,
                expiry_date=item.expiry_date,
                mrp=item.mrp,
                selling_price=item.selling_price,
                quantity=item.quantity,
                discount_amount=item.discount_amount,
                tax_rate=item.tax_rate,
                tax_amount=item_totals["tax_amount"],  # Use calculated value
                line_total=item_totals["line_total"],   # Use calculated value
            )
            for item, item_totals in zip(bill.bill_items, item_totals_list)
        ]
        
        db_bill = Bill(
            user_id=current_user.id,
            customer_id=bill.customer_id,
            bill_number=bill.bill_number,
            bill_date=bill.bill_date,
            sub_total=bill_totals["sub_total"],              
            discount_amount=bill_totals["discount_amount"],  # Use calculated value
            discount_percentage=bill_totals["discount_percentage"],  # Use calculated value
            tax_amount=bill_totals["tax_amount"],            # Use calculated value
            total_amount=bill_totals["total_amount"],        # Use calculated value
            payment_method=bill.payment_method,
            paid_amount=bill.paid_amount,
            balance_amount=bill.balance_amount,
            status=bill.status,
            notes=bill.notes,
            docter_name=bill.docter_name,
            bill_items=bill_items  
        )

        db.add(db_bill)
        await db.commit()
        await db.refresh(db_bill)

        bill_response = schemas.bill.BillResponse.model_validate(db_bill)

        return success_response(
            data=bill_response,
            message="Bill created successfully",
            request=request
        )    
    except NotFoundError:
        await db.rollback()
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while creating bill: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to create bill due to a database error"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error while creating Bill: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while creating bill"
        )    

@router.get("/")
async def getBills(
    request: Request,
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        conditions = [Bill.user_id == current_user.id]
        if search:
            like = f"%{search}%"
            conditions.append(or_(Bill.bill_number.ilike(like), Bill.docter_name.ilike(like), Bill.notes.ilike(like)))

        count_result = await db.execute(select(func.count()).select_from(Bill).where(*conditions))
        total_items = count_result.scalar_one()

        result = await db.execute(
            select(Bill)
            .where(*conditions)
            .order_by(Bill.bill_date.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        db_bills = result.scalars().all()
        bills_response = [schemas.bill.BillResponse.model_validate(b) for b in db_bills]

        return paginated_response(
            data=bills_response,
            page=page,
            page_size=page_size,
            total_items=total_items,
            message="Bills retrieved successfully",
            request=request
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching bills: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to retrieve bills due to a database error"
        )
    except PydanticValidationError as e:
        logger.error(f"Validation error while converting Bills to response: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to process bills data"
        )
    except InternalServerError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching bills: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while retrieving bills"
        )                

@router.get("/{id}")
async def getBill(id: UUID, request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Bill).where(Bill.id == id, Bill.user_id == current_user.id))
        db_bill = result.scalar_one_or_none()
        if not db_bill:
            raise NotFoundError(
                resource="Bill",
                resource_id=str(id)
            )
        bill_response = schemas.bill.BillResponse.model_validate(db_bill)   
        return success_response(
            data=bill_response,
            message="Bill retrieved successfully",
            request=request
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching bill: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to retrieve bill due to a database error"
        )
    except PydanticValidationError as e:
        logger.error(f"Validation error while converting Bill to response: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to process bill data"
        )
    except (InternalServerError, NotFoundError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching bill: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while retrieving bill"
        )


@router.put("/{id}")
async def updateBill(
    id: UUID,
    bill_update: schemas.bill.BillUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Bill).where(Bill.id == id, Bill.user_id == current_user.id))
        db_bill = result.scalar_one_or_none()
        if not db_bill:
            raise NotFoundError(resource="Bill", resource_id=str(id))

        update_data = bill_update.model_dump(exclude_unset=True)

        if "status" in update_data and update_data["status"] not in [s.value for s in BillStatus]:
            raise ValidationError(
                message="Validation failed",
                details=[ErrorDetail(field="status", message=f"Status must be one of: {', '.join(s.value for s in BillStatus)}")]
            )

        for field, value in update_data.items():
            setattr(db_bill, field, value)

        await db.commit()
        await db.refresh(db_bill)

        bill_response = schemas.bill.BillResponse.model_validate(db_bill)
        return success_response(
            data=bill_response,
            message="Bill updated successfully",
            request=request
        )
    except (NotFoundError, ValidationError):
        await db.rollback()
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while updating bill: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to update bill due to a database error"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error while updating bill: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while updating bill"
        )


@router.delete("/{id}")
async def deleteBill(
    id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Bill).where(Bill.id == id, Bill.user_id == current_user.id))
        db_bill = result.scalar_one_or_none()
        if not db_bill:
            raise NotFoundError(resource="Bill", resource_id=str(id))

        await db.delete(db_bill)
        await db.commit()

        return success_response(
            data=None,
            message="Bill deleted successfully",
            request=request
        )
    except NotFoundError:
        await db.rollback()
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while deleting bill: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to delete bill due to a database error"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error while deleting bill: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while deleting bill"
        )