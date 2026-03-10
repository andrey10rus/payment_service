from sqlalchemy import Column, Integer, Numeric, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Order(Base):
    """
    Модель заказа.

    Атрибуты:
    - id: уникальный идентификатор заказа
    - amount: общая сумма заказа
    - paid_amount: сумма, уже оплаченная по заказу
    - status: статус оплаты заказа (not_paid, partial, paid)
    - payments: список связанных платежей
    """

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric)
    paid_amount = Column(Numeric, default=0)
    status = Column(String)

    payments = relationship(
        "Payment",
        back_populates="order",
        lazy="selectin",
    )


class Payment(Base):
    """
    Модель платежа.

    Атрибуты:
    - id: уникальный идентификатор платежа
    - order_id: ID заказа, к которому относится платеж
    - amount: сумма платежа
    - type: тип платежа (cash, acquiring)
    - status: статус платежа (pending, paid, refunded)
    - bank_payment_id: уникальный идентификатор платежа в банке (для acquiring)
    - order: объект заказа, к которому привязан платеж
    """

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"))

    amount = Column(Numeric)

    type = Column(String)

    status = Column(String)

    bank_payment_id = Column(String, nullable=True)

    order = relationship(
        "Order",
        back_populates="payments",
        lazy="selectin",
    )
