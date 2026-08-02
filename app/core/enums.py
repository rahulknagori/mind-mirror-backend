from enum import Enum
from decimal import Decimal


class BillStatus(str, Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PurchaseStatus(str, Enum):
    DRAFT = "draft"
    ORDERED = "ordered"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"
    RETURNED = "returned"


GST_RATES = [Decimal("0"), Decimal("5"), Decimal("12"), Decimal("18")]
