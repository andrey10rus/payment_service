from pydantic import BaseModel, Field
from decimal import Decimal
from .enums import PaymentType


class PaymentCreate(BaseModel):
    order_id: int = Field(..., description="ID заказа, к которому привязывается платеж")
    amount: Decimal = Field(..., description="Сумма платежа")
    type: PaymentType = Field(..., description="Тип платежа (cash, acquiring и т.д.)")


class PaymentResponse(BaseModel):
    id: int = Field(..., description="ID платежа")
    order_id: int = Field(..., description="ID заказа, к которому относится платеж")
    amount: Decimal = Field(..., description="Сумма платежа")
    status: str = Field(
        ..., description="Статус платежа (not_paid, partial, paid, refunded)"
    )
    type: str = Field(..., description="Тип платежа")
