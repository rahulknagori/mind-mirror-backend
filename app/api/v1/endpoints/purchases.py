import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .... import schemas
from ....api.deps import get_current_user
from ....core.database import get_db
from ....core.enums import PurchaseStatus
from ....core.exceptions import ErrorDetail, InternalServerError, NotFoundError, ValidationError
from ....core.response import paginated_response, success_response
from ....models.medicine import Medicine
from ....models.purchase import Purchase
from ....models.purchase_item import PurchaseItem
from ....models.user import User
from ....services.medicine_service import MedicineService
from ....services.purchase_service import PurchaseService
from ....services.supplier_service import SupplierService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/")
async def create_purchase(
    purchase: schemas.purchase.PurchaseCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        if purchase.status is not None and purchase.status not in [s.value for s in PurchaseStatus]:
            raise ValidationError(
                message="Validation failed",
                details=[ErrorDetail(field="status", message=f"Status must be one of: {', '.join(s.value for s in PurchaseStatus)}")]
            )

        await SupplierService.validate_supplier_exists(
            db=db,
            supplier_id=purchase.supplier_id,
            user_id=current_user.id
        )

        medicines_by_id = {}
        for item in purchase.purchase_items:
            medicines_by_id[item.medicine_id] = await MedicineService.validate_medicine_exists(
                db=db,
                medicine_id=item.medicine_id,
                user_id=current_user.id
            )

        item_totals_list, purchase_totals = PurchaseService.calculate_all_totals(purchase)

        purchase_items = [
            PurchaseItem(
                medicine_id=item.medicine_id,
                medicine_name=item.medicine_name,
                batch_number=item.batch_number,
                expiry_date=item.expiry_date,
                mrp=item.mrp,
                purchase_price=item.purchase_price,
                quantity=item.quantity,
                discount_amount=item.discount_amount,
                tax_rate=item.tax_rate,
                tax_amount=item_totals["tax_amount"],
                line_total=item_totals["line_total"],
            )
            for item, item_totals in zip(purchase.purchase_items, item_totals_list)
        ]

        db_purchase = Purchase(
            user_id=current_user.id,
            supplier_id=purchase.supplier_id,
            purchase_number=purchase.purchase_number,
            purchase_date=purchase.purchase_date,
            sub_total=purchase_totals["sub_total"],
            discount_amount=purchase_totals["discount_amount"],
            discount_percentage=purchase_totals["discount_percentage"],
            tax_amount=purchase_totals["tax_amount"],
            total_amount=purchase_totals["total_amount"],
            payment_method=purchase.payment_method,
            paid_amount=purchase.paid_amount,
            balance_amount=purchase.balance_amount,
            status=purchase.status,
            notes=purchase.notes,
            purchase_items=purchase_items
        )

        if purchase.status == PurchaseStatus.RECEIVED.value:
            for item in purchase.purchase_items:
                medicines_by_id[item.medicine_id].stock_quantity += item.quantity

        db.add(db_purchase)
        await db.commit()
        await db.refresh(db_purchase)

        purchase_response = schemas.purchase.PurchaseResponse.model_validate(db_purchase)

        return success_response(
            data=purchase_response,
            message="Purchase created successfully",
            request=request
        )
    except (NotFoundError, ValidationError):
        await db.rollback()
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while creating purchase: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to create purchase due to a database error"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error while creating purchase: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while creating purchase"
        )


@router.get("/")
async def get_purchases(
    request: Request,
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        conditions = [Purchase.user_id == current_user.id]
        if search:
            like = f"%{search}%"
            conditions.append(or_(Purchase.purchase_number.ilike(like), Purchase.notes.ilike(like)))

        count_result = await db.execute(select(func.count()).select_from(Purchase).where(*conditions))
        total_items = count_result.scalar_one()

        result = await db.execute(
            select(Purchase)
            .where(*conditions)
            .order_by(Purchase.purchase_date.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        db_purchases = result.scalars().all()
        purchases_response = [schemas.purchase.PurchaseResponse.model_validate(p) for p in db_purchases]

        return paginated_response(
            data=purchases_response,
            page=page,
            page_size=page_size,
            total_items=total_items,
            message="Purchases retrieved successfully",
            request=request
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching purchases: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to retrieve purchases due to a database error"
        )
    except PydanticValidationError as e:
        logger.error(f"Validation error while converting purchases to response: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to process purchases data"
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching purchases: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while retrieving purchases"
        )


@router.get("/{id}")
async def get_purchase(
    id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Purchase).where(Purchase.id == id, Purchase.user_id == current_user.id))
        db_purchase = result.scalar_one_or_none()
        if not db_purchase:
            raise NotFoundError(resource="Purchase", resource_id=str(id))

        purchase_response = schemas.purchase.PurchaseResponse.model_validate(db_purchase)
        return success_response(
            data=purchase_response,
            message="Purchase retrieved successfully",
            request=request
        )
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching purchase: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to retrieve purchase due to a database error"
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching purchase: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while retrieving purchase"
        )


@router.put("/{id}")
async def update_purchase(
    id: UUID,
    purchase_update: schemas.purchase.PurchaseUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Purchase).where(Purchase.id == id, Purchase.user_id == current_user.id))
        db_purchase = result.scalar_one_or_none()
        if not db_purchase:
            raise NotFoundError(resource="Purchase", resource_id=str(id))

        update_data = purchase_update.model_dump(exclude_unset=True)

        if "status" in update_data and update_data["status"] not in [s.value for s in PurchaseStatus]:
            raise ValidationError(
                message="Validation failed",
                details=[ErrorDetail(field="status", message=f"Status must be one of: {', '.join(s.value for s in PurchaseStatus)}")]
            )

        for field, value in update_data.items():
            setattr(db_purchase, field, value)

        await db.commit()
        await db.refresh(db_purchase)

        purchase_response = schemas.purchase.PurchaseResponse.model_validate(db_purchase)
        return success_response(
            data=purchase_response,
            message="Purchase updated successfully",
            request=request
        )
    except (NotFoundError, ValidationError):
        await db.rollback()
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while updating purchase: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to update purchase due to a database error"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error while updating purchase: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while updating purchase"
        )


@router.delete("/{id}")
async def delete_purchase(
    id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(Purchase).where(Purchase.id == id, Purchase.user_id == current_user.id)
        )
        db_purchase = result.scalar_one_or_none()
        if not db_purchase:
            raise NotFoundError(resource="Purchase", resource_id=str(id))

        if db_purchase.status == PurchaseStatus.RECEIVED.value:
            items_result = await db.execute(select(PurchaseItem).where(PurchaseItem.purchase_id == db_purchase.id))
            db_items = items_result.scalars().all()
            for db_item in db_items:
                medicine = await MedicineService.validate_medicine_exists(
                    db=db,
                    medicine_id=db_item.medicine_id,
                    user_id=current_user.id
                )
                medicine.stock_quantity -= db_item.quantity

        await db.delete(db_purchase)
        await db.commit()

        return success_response(
            data=None,
            message="Purchase deleted successfully",
            request=request
        )
    except NotFoundError:
        await db.rollback()
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while deleting purchase: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="Failed to delete purchase due to a database error"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error while deleting purchase: {str(e)}", exc_info=True)
        raise InternalServerError(
            message="An unexpected error occurred while deleting purchase"
        )
