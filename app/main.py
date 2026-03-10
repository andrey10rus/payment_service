from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.future import select

from .database import Base, engine, AsyncSessionLocal
from .api import payments
from .models import Order
from .enums import PaymentStatus
from decimal import Decimal


@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Создание тестового заказа, если ни одного нет
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Order))
        order_exists = result.scalars().first()
        if not order_exists:
            order = Order(
                amount=Decimal(1000),
                paid_amount=Decimal(0),
                status=PaymentStatus.NOT_PAID.value,
            )
            db.add(order)
            await db.commit()

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(payments.router)
