from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Order, Payment
from ..enums import PaymentStatus, PaymentType
from .bank_api import BankAPI

bank_api = BankAPI()


class PaymentService:
    """
    Сервис работы с платежами по заказу.
    Поддерживает асинхронное взаимодействие с базой и внешним API банка.
    """

    @staticmethod
    def update_order_status(order: Order) -> None:
        """
        Обновляет статус заказа на основе оплаченной суммы.
        """
        if order.paid_amount == 0:
            order.status = PaymentStatus.NOT_PAID.value
        elif order.paid_amount < order.amount:
            order.status = PaymentStatus.PARTIAL.value
        else:
            order.status = PaymentStatus.PAID.value

    async def get_payment(self, db: AsyncSession, payment_id: int) -> Payment:

        payment: Payment | None = await db.get(Payment, payment_id)

        if not payment:
            raise ValueError("payment not found")

        acquiring = await bank_api.acquiring_check(payment)

        bank_status = acquiring.get("status")

        if bank_status and payment.status != bank_status:
            payment.status = bank_status
            await db.commit()
            await db.refresh(payment)

        return payment

    async def get_payments(
        self,
        db: AsyncSession,
        order_id: int | None = None,
    ) -> list[Payment]:

        query = select(Payment)

        if order_id is not None:
            query = query.where(Payment.order_id == order_id)

        result = await db.execute(query)
        payments = result.scalars().all()

        for payment in payments:

            acquiring = await bank_api.acquiring_check(payment)
            bank_status = acquiring.get("status")

            if bank_status and bank_status != payment.status:
                payment.status = bank_status

        await db.commit()

        return payments

    async def deposit(
        self,
        db: AsyncSession,
        order_id: int,
        amount: Decimal,
        payment_type: PaymentType,
    ) -> Payment:
        """
        Создает платеж по заказу.
        """

        order: Order | None = await db.get(Order, order_id)
        if not order:
            raise ValueError("order not found")

        if order.paid_amount + amount > order.amount:
            raise ValueError("payment exceeds order amount")

        payment = Payment(
            order_id=order_id,
            amount=amount,
            type=payment_type.value,
            status=PaymentStatus.PENDING.value,
        )

        bank_id = await bank_api.acquiring_start(order_id, amount)
        payment.bank_payment_id = bank_id

        payment.status = PaymentStatus.PAID.value
        order.paid_amount += amount

        db.add(payment)
        self.update_order_status(order)

        await db.commit()
        await db.refresh(payment)

        return payment

    async def refund(self, db: AsyncSession, payment_id: int) -> Payment:
        """
        Возврат платежа.
        Только для уже оплаченных.
        """
        payment: Payment | None = await db.get(Payment, payment_id)
        if payment is None:
            raise ValueError("payment not found")

        acquiring = await bank_api.acquiring_check(payment)
        bank_status = acquiring.get("status")

        if bank_status and payment.status != bank_status:
            payment.status = bank_status

        if payment.status != PaymentStatus.PAID.value:
            raise ValueError("only paid payments can be refunded")

        order: Order = payment.order

        payment.status = PaymentStatus.REFUNDED.value
        order.paid_amount -= payment.amount

        self.update_order_status(order)

        await db.commit()
        await db.refresh(payment)

        return payment
