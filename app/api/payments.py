from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas import PaymentCreate, PaymentResponse
from ..services.payment_service import PaymentService

router = APIRouter()

service = PaymentService()


@router.get(
    "/payments/{payment_id}",
    responses={
        404: {"description": "Платеж не найден"},
        200: {"description": "Платеж получен успешно"},
    },
)
async def get_payment(
    payment_id: int, db: AsyncSession = Depends(get_db)
) -> PaymentResponse:
    """
    Получить платеж по payment_id.

    Аргументы:
    - payment_id: id платежа
    """

    try:

        payment = await service.get_payment(db, payment_id)

        return payment

    except ValueError as e:

        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/payments",
    responses={
        200: {"description": "Список платежей получен успешно"},
    },
)
async def get_payments(
    order_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[PaymentResponse]:
    """
    Получить список платежей.

    Аргументы:
    - order_id (опционально): id заказа для фильтрации платежей
    """

    payments = await service.get_payments(db, order_id)

    return payments


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
    Возврат платежа по payment_id

    Аргументы:
    - payment_id: id платежа
    """
    try:

        payment = await service.refund(db, payment_id)

        return payment

    except ValueError as e:

        raise HTTPException(status_code=400, detail=str(e))
