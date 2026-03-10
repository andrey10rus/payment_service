import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from httpx import AsyncClient, ASGITransport
from app.settings import Settings

settings = Settings()

TEST_DATABASE_URL = settings.TEST_DATABASE_URL

engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)

AsyncTestingSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_db_session(prepare_db):
    async with AsyncTestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def async_client():
    async def override_get_db():
        async with AsyncTestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
