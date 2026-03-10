import pytest
from unittest.mock import patch
from decimal import Decimal
from app.models import Order
from app.enums import PaymentStatus, PaymentType

pytestmark = pytest.mark.asyncio


async def test_create_cash_payment(async_client, async_db_session):
    order = Order(amount=1000, paid_amount=0, status=PaymentStatus.NOT_PAID.value)
    async_db_session.add(order)
    await async_db_session.commit()
    await async_db_session.refresh(order)

    # Патчим BankAPI.acquiring_start, чтобы исключить случайные ошибки random.random()
    with patch(
        "app.services.bank_api.BankAPI.acquiring_start", return_value="fake-payment-id"
    ):
        response = await async_client.post(
            "/payments",
            json={"order_id": order.id, "amount": 200, "type": PaymentType.CASH.value},
        )

    assert response.status_code == 200
    data = response.json()
    assert Decimal(data["amount"]) == Decimal("200")
    assert data["status"] == PaymentStatus.PAID.value


async def test_refund(async_client, async_db_session):
    order = Order(amount=1000, paid_amount=0, status=PaymentStatus.NOT_PAID.value)
    async_db_session.add(order)
    await async_db_session.commit()
    await async_db_session.refresh(order)

    payment_response = await async_client.post(
        "/payments",
        json={"order_id": order.id, "amount": 200, "type": PaymentType.CASH.value},
    )
    assert payment_response.status_code == 200
    payment_data = payment_response.json()
    assert payment_data["status"] == PaymentStatus.PAID.value

    payment_id = payment_data["id"]

    refund_response = await async_client.post(f"/payments/{payment_id}/refund")
    assert refund_response.status_code == 200

    refund_data = refund_response.json()
    assert refund_data["status"] == PaymentStatus.REFUNDED.value
    assert Decimal(refund_data["amount"]) == Decimal("200")
