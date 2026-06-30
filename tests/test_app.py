import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import get_db


@pytest.mark.asyncio
async def test_get_db():
    gen = get_db()
    session = await gen.__anext__()
    assert isinstance(session, AsyncSession)
    await gen.aclose()

@pytest.mark.asyncio
async def test_get_books(client: AsyncClient):
    r = await client.get("/books")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 5
    for book in data:
        assert "price" in book
        assert isinstance(book["price"], int)

@pytest.mark.asyncio
async def test_post_order(client: AsyncClient):
    r = await client.post("/order", json={"user_id": 1, "book_id": 1})
    assert r.status_code == 201
    data = r.json()
    assert data["user_id"] == 1
    assert data["book_id"] == 1
    assert data["status"] == "pending"
    assert "id" in data

@pytest.mark.asyncio
async def test_post_order_bad_book(client: AsyncClient):
    r = await client.post("/order", json={"user_id": 1, "book_id": 999})
    assert r.status_code == 404
