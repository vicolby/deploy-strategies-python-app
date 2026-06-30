import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")

import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.database import Base
from app.main import app, get_db
from app.seed import seed_books


@pytest_asyncio.fixture
async def client():
    with PostgresContainer("postgres:16", driver="asyncpg") as postgres:
        url = postgres.get_connection_url().replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        engine = create_async_engine(url, echo=False, future=True)
        session_maker = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        import app.main as main_module

        main_module.engine = engine
        main_module.AsyncSessionLocal = session_maker

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with session_maker() as session:
            await seed_books(session)

        async def override_get_db():
            async with session_maker() as session:
                yield session

        app.dependency_overrides[get_db] = override_get_db

        async with LifespanManager(app) as manager:
            transport = ASGITransport(app=manager.app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as ac:
                yield ac

        await engine.dispose()
        app.dependency_overrides.clear()
