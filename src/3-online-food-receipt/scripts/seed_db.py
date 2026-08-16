"""Populate the database with sample receipts spanning the last month.

Usage:
    uv run python scripts/seed_db.py [--days 30] [--seed 42] [--clear]
"""

import argparse
import random
import sys
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.adapters import build_connection_pool, init_schema  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.domain.entities import Item, ParsedReceipt  # noqa: E402
from app.infrastructure.db_repo import PostgresReceiptRepository  # noqa: E402

PLACES_MENU: dict[str, list[tuple[str, int]]] = {
    "Warung Nasi Padang Sederhana": [
        ("Nasi Rendang", 25000),
        ("Nasi Ayam Goreng", 20000),
        ("Es Teh Manis", 5000),
        ("Sayur Nangka", 8000),
    ],
    "Bakso Lava Malang": [
        ("Bakso Urat", 18000),
        ("Mie Ayam Bakso", 22000),
        ("Es Jeruk", 6000),
    ],
    "Kopi Kenangan": [
        ("Kopi Kenangan Mantan", 18000),
        ("Croissant Butter", 15000),
        ("Americano", 20000),
    ],
    "Geprek Bensu": [
        ("Ayam Geprek Original", 17000),
        ("Ayam Geprek Keju", 22000),
        ("Es Teh", 4000),
        ("Nasi Putih", 5000),
    ],
    "Solaria": [
        ("Nasi Goreng Spesial", 28000),
        ("Ayam Bakar", 32000),
        ("Jus Alpukat", 15000),
    ],
    "Sate Khas Senayan": [
        ("Sate Ayam", 35000),
        ("Sate Kambing", 45000),
        ("Lontong", 8000),
        ("Es Kelapa Muda", 12000),
    ],
    "Pizza Hut Delivery": [
        ("Pizza Personal Pan", 55000),
        ("Chicken Wings", 40000),
        ("Coke", 10000),
    ],
    "McDonald's": [
        ("Big Mac", 35000),
        ("McFlurry", 18000),
        ("French Fries", 20000),
        ("Coke", 10000),
    ],
    "Chatime": [
        ("Brown Sugar Fresh Milk", 25000),
        ("QQ Milk Tea", 22000),
    ],
    "Gudeg Yu Djum": [
        ("Gudeg Komplit", 30000),
        ("Krecek", 10000),
        ("Teh Tawar Hangat", 4000),
    ],
}


def generate_receipt(rng: random.Random, transaction_date: date) -> ParsedReceipt:
    place, menu = rng.choice(list(PLACES_MENU.items()))
    picks = rng.sample(menu, k=rng.randint(1, min(4, len(menu))))

    items = [
        Item(name=name, price=float(price), quantity=rng.randint(1, 2))
        for name, price in picks
    ]
    total = sum(item.price * item.quantity for item in items)

    return ParsedReceipt(
        place=place,
        transaction_date=transaction_date,
        total=total,
        items=items,
    )


def seed(
    repository: PostgresReceiptRepository,
    days: int,
    rng: random.Random,
) -> int:
    today = date.today()
    start = today - timedelta(days=days)

    count = 0
    for offset in range(days + 1):
        day = start + timedelta(days=offset)
        for _ in range(rng.choices([0, 1, 2, 3], weights=[1, 4, 3, 1])[0]):
            parsed = generate_receipt(rng, day)
            image_path = f"data/receipts/seed_{uuid4().hex}.jpg"
            repository.save(parsed, image_path)
            count += 1

    return count


def clear_receipts(pool) -> None:
    with pool.connection() as conn:
        conn.execute("TRUNCATE TABLE receipt_items, receipts RESTART IDENTITY CASCADE")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--days", type=int, default=30, help="How many days back from today to seed (default: 30)"
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument(
        "--clear", action="store_true", help="Delete existing receipts before seeding"
    )
    args = parser.parse_args()

    settings = get_settings()
    pool = build_connection_pool(
        dsn=settings.database.dsn,
        min_size=settings.database.min_pool_size,
        max_size=settings.database.max_pool_size,
    )
    init_schema(pool)

    if args.clear:
        clear_receipts(pool)
        print("Cleared existing receipts.")

    repository = PostgresReceiptRepository(pool=pool)
    rng = random.Random(args.seed)

    inserted = seed(repository, days=args.days, rng=rng)
    print(f"Inserted {inserted} receipts spanning {args.days} days (through {date.today()}).")

    pool.close()


if __name__ == "__main__":
    main()
