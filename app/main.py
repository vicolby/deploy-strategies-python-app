import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base, build_database
from app.models import Book, Order
from app.schemas import BookOut, OrderIn, OrderOut
from app.seed import seed_books

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/toydb",
)

engine, AsyncSessionLocal = build_database(DATABASE_URL)

provider = TracerProvider()
trace.set_tracer_provider(provider)
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Book))
        if not result.scalars().first():
            await seed_books(session)
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument()
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)

async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/books", response_model=list[BookOut])
async def list_books(db: AsyncSession = Depends(get_db)) -> list[BookOut]:
    result = await db.execute(select(Book))
    return list(result.scalars().all())

@app.post("/order", response_model=OrderOut, status_code=201)
async def create_order(data: OrderIn, db: AsyncSession = Depends(get_db)) -> OrderOut:
    book = await db.get(Book, data.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    order = Order(user_id=data.user_id, book_id=data.book_id)
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order
