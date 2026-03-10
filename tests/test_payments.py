import pytest
from unittest.mock import patch
from decimal import Decimal
from app.models import Order, Payment
from app.enums import PaymentStatus, PaymentType

pytestmark = pytest.mark.asyncio


async def test_get_payment(async_client, async_db_session):
    order = Order(amount=1000, paid_amount=200, status=PaymentStatus.PARTIAL.value)
    async_db_session.add(order)
    await async_db_session.commit()
    await async_db_session.refresh(order)

    payment = Payment(
        order_id=order.id,
        amount=200,
        type=PaymentType.CASH.value,
        status=PaymentStatus.PAID.value,
    )

    async_db_session.add(payment)
    await async_db_session.commit()
    await async_db_session.refresh(payment)

    with patch(
        "app.services.bank_api.BankAPI.acquiring_check",
        return_value={"status": PaymentStatus.PAID.value},
    ):
        response = await async_client.get(f"/payments/{payment.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == payment.id
    assert Decimal(data["amount"]) == Decimal("200")
    assert data["status"] == PaymentStatus.PAID.value


async def test_get_payment_not_found(async_client, async_db_session):
    response = await async_client.get("/payments/999999")

    assert response.status_code == 404


async def test_get_payments_by_order(async_client, async_db_session):
    order = Order(amount=1000, paid_amount=400, status=PaymentStatus.PARTIAL.value)
    async_db_session.add(order)
    await async_db_session.commit()
    await async_db_session.refresh(order)

    payment1 = Payment(
        order_id=order.id,
        amount=200,
        type=PaymentType.CASH.value,
        status=PaymentStatus.PAID.value,
    )

    payment2 = Payment(
        order_id=order.id,
        amount=200,
        type=PaymentType.ACQUIRING.value,
        status=PaymentStatus.PAID.value,
    )

    async_db_session.add_all([payment1, payment2])
    await async_db_session.commit()

    with patch(
        "app.services.bank_api.BankAPI.acquiring_check",
        return_value={"status": PaymentStatus.PAID.value},
    ):
        response = await async_client.get(f"/payments?order_id={order.id}")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2

    amounts = [Decimal(p["amount"]) for p in data]
    assert Decimal("200") in amounts


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
