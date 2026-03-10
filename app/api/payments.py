from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas import PaymentCreate, PaymentResponse
from ..services.payment_service import PaymentService

router = APIRouter()

service = PaymentService()


@router.post(
    "/payments",
    responses={
        502: {"description": "Ошибка внешнего сервиса банка"},
        400: {"description": "Ошибка в переданных аргументах"},
        200: {"description": "Платеж создан успешно"},
    },
)
async def create_payment(
    data: PaymentCreate, db: AsyncSession = Depends(get_db)
) -> PaymentResponse:
    """
    Создаёт платеж для указанного заказа.

    Аргументы:
    - data (PaymentCreate): данные платежа, включая order_id, amount и тип платежа.
    """

    try:

        payment = await service.deposit(db, data.order_id, data.amount, data.type)

        return payment

    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/payments/{payment_id}/refund",
    responses={
        400: {"description": "Ошибка в переданных аргументах"},
        200: {"description": "успешно"},
    },
)
async def refund(
    payment_id: int, db: AsyncSession = Depends(get_db)
) -> PaymentResponse:
    """
    Создаёт платеж для указанного заказа.

    Аргументы:
    - payment_id: id платежа
    """
    try:

        payment = await service.refund(db, payment_id)

        return payment

    except ValueError as e:

        raise HTTPException(status_code=400, detail=str(e))
