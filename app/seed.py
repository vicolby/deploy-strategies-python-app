import random

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Book


async def seed_books(session: AsyncSession) -> None:
    books = [
        Book(
            title="1984",
            author="George Orwell",
            price=random.randint(500, 5000),
        ),
        Book(
            title="Dune",
            author="Frank Herbert",
            price=random.randint(500, 5000),
        ),
        Book(
            title="Neuromancer",
            author="William Gibson",
            price=random.randint(500, 5000),
        ),
        Book(
            title="Snow Crash",
            author="Neal Stephenson",
            price=random.randint(500, 5000),
        ),
        Book(
            title="Foundation",
            author="Isaac Asimov",
            price=random.randint(500, 5000),
        ),
    ]
    session.add_all(books)
    await session.commit()
