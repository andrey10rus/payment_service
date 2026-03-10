from enum import Enum


class PaymentType(str, Enum):
    CASH = "cash"
    ACQUIRING = "acquiring"


class PaymentStatus(str, Enum):
    NOT_PAID = "not_paid"
    PARTIAL = "partial"
    PAID = "paid"
    PENDING = "pending"
    REFUNDED = "refunded"
    FAILED = "failed"
