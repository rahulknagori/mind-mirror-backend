from decimal import Decimal
from typing import List, Dict, Tuple
from .. import schemas


class BillService:
    """Service for bill-related business logic and calculations"""
    
    @staticmethod
    def calculate_item_totals(item_data: schemas.bill_item.BillItemCreate) -> Dict[str, Decimal]:
        """
        Calculate tax_amount and line_total for a single bill item.
        
        Args:
            item_data: BillItemCreate object with selling_price, quantity, tax_rate, discount_amount
            
        Returns:
            Dictionary with calculated tax_amount and line_total
        """
        # Calculate item subtotal (price * quantity)
        item_subtotal = item_data.selling_price * item_data.quantity
        
        # Calculate tax amount: (subtotal * tax_rate / 100)
        tax_amount = (item_subtotal * item_data.tax_rate) / Decimal("100")
        
        # Calculate line total: subtotal - discount + tax
        line_total = item_subtotal - item_data.discount_amount + tax_amount
        
        # Ensure non-negative values
        tax_amount = max(tax_amount, Decimal("0"))
        line_total = max(line_total, Decimal("0"))
        
        return {
            "tax_amount": tax_amount,
            "line_total": line_total
        }
    
    @staticmethod
    def calculate_bill_totals(items: List[schemas.bill_item.BillItemCreate], item_totals_list: List[Dict[str, Decimal]] = None) -> Dict[str, Decimal]:
        """
        Calculate all bill-level totals from a list of items.
        
        Args:
            items: List of BillItemCreate objects
            item_totals_list: Optional pre-calculated item totals to avoid recalculation
            
        Returns:
            Dictionary with sub_total, discount_amount, tax_amount, total_amount, discount_percentage
        """
        # Calculate sub_total: sum of (selling_price * quantity) for all items
        sub_total = sum(
            item.selling_price * item.quantity 
            for item in items
        )
        
        # Calculate total discount: sum of all item discounts
        discount_amount = sum(
            item.discount_amount 
            for item in items
        )
        
        # Calculate total tax: use pre-calculated totals if provided, otherwise calculate
        if item_totals_list:
            total_tax_amount = sum(
                item_totals["tax_amount"] 
                for item_totals in item_totals_list
            )
        else:
            total_tax_amount = Decimal("0")
            for item in items:
                item_totals = BillService.calculate_item_totals(item)
                total_tax_amount += item_totals["tax_amount"]
        
        # Calculate total amount: sub_total - discount + tax
        total_amount = sub_total - discount_amount + total_tax_amount
        
        # Calculate discount percentage: (discount_amount / sub_total) * 100
        # Handle division by zero
        if sub_total > 0:
            discount_percentage = (discount_amount / sub_total) * Decimal("100")
        else:
            discount_percentage = Decimal("0")
        
        # Ensure non-negative values
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
    def calculate_all_totals(bill_data: schemas.bill.BillCreate) -> Tuple[List[Dict[str, Decimal]], Dict[str, Decimal]]:
        """
        Calculate all item-level and bill-level totals.
        
        Args:
            bill_data: BillCreate object with bill_items
            
        Returns:
            Tuple of (list of item totals dicts, bill totals dict)
        """
        # Calculate totals for each item
        item_totals_list = []
        for item in bill_data.bill_items:
            item_totals = BillService.calculate_item_totals(item)
            item_totals_list.append(item_totals)
        
        # Calculate bill-level totals using pre-calculated item totals
        bill_totals = BillService.calculate_bill_totals(bill_data.bill_items, item_totals_list)
        
        return item_totals_list, bill_totals
