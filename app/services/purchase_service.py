from decimal import Decimal
from typing import List, Dict, Tuple
from .. import schemas


class PurchaseService:
    """Service for purchase-related business logic and calculations"""

    @staticmethod
    def calculate_item_totals(item_data: schemas.purchase_item.PurchaseItemCreate) -> Dict[str, Decimal]:
        """
        Calculate tax_amount and line_total for a single purchase item.

        Args:
            item_data: PurchaseItemCreate object with purchase_price, quantity, tax_rate, discount_amount

        Returns:
            Dictionary with calculated tax_amount and line_total
        """
        item_subtotal = item_data.purchase_price * item_data.quantity

        tax_amount = (item_subtotal * item_data.tax_rate) / Decimal("100")

        line_total = item_subtotal - item_data.discount_amount + tax_amount

        tax_amount = max(tax_amount, Decimal("0"))
        line_total = max(line_total, Decimal("0"))

        return {
            "tax_amount": tax_amount,
            "line_total": line_total
        }

    @staticmethod
    def calculate_purchase_totals(items: List[schemas.purchase_item.PurchaseItemCreate], item_totals_list: List[Dict[str, Decimal]] = None) -> Dict[str, Decimal]:
        """
        Calculate all purchase-level totals from a list of items.

        Args:
            items: List of PurchaseItemCreate objects
            item_totals_list: Optional pre-calculated item totals to avoid recalculation

        Returns:
            Dictionary with sub_total, discount_amount, tax_amount, total_amount, discount_percentage
        """
        sub_total = sum(
            item.purchase_price * item.quantity
            for item in items
        )

        discount_amount = sum(
            item.discount_amount
            for item in items
        )

        if item_totals_list:
            total_tax_amount = sum(
                item_totals["tax_amount"]
                for item_totals in item_totals_list
            )
        else:
            total_tax_amount = Decimal("0")
            for item in items:
                item_totals = PurchaseService.calculate_item_totals(item)
                total_tax_amount += item_totals["tax_amount"]

        total_amount = sub_total - discount_amount + total_tax_amount

        if sub_total > 0:
            discount_percentage = (discount_amount / sub_total) * Decimal("100")
        else:
            discount_percentage = Decimal("0")

        sub_total = max(sub_total, Decimal("0"))
        discount_amount = max(discount_amount, Decimal("0"))
        total_tax_amount = max(total_tax_amount, Decimal("0"))
        total_amount = max(total_amount, Decimal("0"))
        discount_percentage = max(discount_percentage, Decimal("0"))

        return {
            "sub_total": sub_total,
            "discount_amount": discount_amount,
            "tax_amount": total_tax_amount,
            "total_amount": total_amount,
            "discount_percentage": discount_percentage
        }

    @staticmethod
    def calculate_all_totals(purchase_data: schemas.purchase.PurchaseCreate) -> Tuple[List[Dict[str, Decimal]], Dict[str, Decimal]]:
        """
        Calculate all item-level and purchase-level totals.

        Args:
            purchase_data: PurchaseCreate object with purchase_items

        Returns:
            Tuple of (list of item totals dicts, purchase totals dict)
        """
        item_totals_list = []
        for item in purchase_data.purchase_items:
            item_totals = PurchaseService.calculate_item_totals(item)
            item_totals_list.append(item_totals)

        purchase_totals = PurchaseService.calculate_purchase_totals(purchase_data.purchase_items, item_totals_list)

        return item_totals_list, purchase_totals
