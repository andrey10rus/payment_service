import uuid
import random
from ..models import Payment
from decimal import Decimal
from ..enums import PaymentStatus


class BankAPI:

    # эмуляция запроса к bank.api/acquiring_start
    async def acquiring_start(self, order_id: int, amount: Decimal):

        # имитация ошибки
        if random.random() < 0.05:
            raise ConnectionError("bank error")

        return str(uuid.uuid4())

    # эмуляция запроса к bank.api/acquiring_check
    async def acquiring_check(self, payment: Payment):

        return {
            "payment_id": payment.bank_payment_id,
            "status": (
                "paid" if payment.status != PaymentStatus.REFUNDED else "refunded"
            ),
        }
