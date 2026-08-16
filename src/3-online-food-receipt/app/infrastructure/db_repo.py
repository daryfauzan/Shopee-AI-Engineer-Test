from datetime import date

from psycopg import Connection
from psycopg_pool import ConnectionPool

from app.domain.entities import Item, ParsedReceipt, Receipt
from app.domain.repositories import ReceiptRepository


class PostgresReceiptRepository(ReceiptRepository):
    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def save(self, parsed: ParsedReceipt, image_path: str) -> Receipt:
        with self._pool.connection() as conn:
            receipt_id, uploaded_at = conn.execute(
                """
                INSERT INTO receipts (place, transaction_date, total, image_path)
                VALUES (%s, %s, %s, %s)
                RETURNING id, uploaded_at
                """,
                (parsed.place, parsed.transaction_date, parsed.total, image_path),
            ).fetchone()

            items: list[Item] = []
            for item in parsed.items:
                (item_id,) = conn.execute(
                    """
                    INSERT INTO receipt_items (receipt_id, name, price, quantity)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (receipt_id, item.name, item.price, item.quantity),
                ).fetchone()
                items.append(item.model_copy(update={"id": item_id}))

        return Receipt(
            id=receipt_id,
            place=parsed.place,
            uploaded_at=uploaded_at,
            transaction_date=parsed.transaction_date,
            total=parsed.total,
            image_path=image_path,
            items=items,
        )

    def get_by_id(self, receipt_id: int) -> Receipt | None:
        with self._pool.connection() as conn:
            row = conn.execute(
                """
                SELECT id, place, uploaded_at, transaction_date, total, image_path
                FROM receipts WHERE id = %s
                """,
                (receipt_id,),
            ).fetchone()
            if row is None:
                return None
            return self._hydrate_many(conn, [row])[0]

    def list_all(self) -> list[Receipt]:
        with self._pool.connection() as conn:
            rows = conn.execute(
                """
                SELECT id, place, uploaded_at, transaction_date, total, image_path
                FROM receipts ORDER BY uploaded_at DESC
                """
            ).fetchall()
            return self._hydrate_many(conn, rows)

    def search(
        self,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        food_name: str | None = None,
        place: str | None = None,
    ) -> list[Receipt]:
        clauses, params = self._match_clauses(start_date, end_date, food_name, place)
        joins = "JOIN receipt_items i ON i.receipt_id = r.id" if food_name else ""
        query = f"""
            SELECT DISTINCT r.id, r.place, r.uploaded_at, r.transaction_date, r.total, r.image_path
            FROM receipts r
            {joins}
            WHERE {clauses}
            ORDER BY r.transaction_date DESC NULLS LAST, r.uploaded_at DESC
        """
        with self._pool.connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return self._hydrate_many(conn, rows)

    def total_amount(
        self,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        food_name: str | None = None,
        place: str | None = None,
    ) -> float:
        clauses, params = self._match_clauses(start_date, end_date, food_name, place)
        if food_name:
            # Sum only the matching line items, not the whole receipt total.
            query = f"""
                SELECT COALESCE(SUM(i.price * i.quantity), 0)
                FROM receipt_items i
                JOIN receipts r ON r.id = i.receipt_id
                WHERE {clauses}
            """
        else:
            query = f"""
                SELECT COALESCE(SUM(r.total), 0)
                FROM receipts r
                WHERE {clauses}
            """
        with self._pool.connection() as conn:
            (total,) = conn.execute(query, params).fetchone()
        return round(float(total), 2)

    @staticmethod
    def _match_clauses(
        start_date: date | None,
        end_date: date | None,
        food_name: str | None,
        place: str | None,
    ) -> tuple[str, list]:
        clauses = ["1 = 1"]
        params: list = []
        if start_date is not None:
            clauses.append("r.transaction_date >= %s")
            params.append(start_date)
        if end_date is not None:
            clauses.append("r.transaction_date <= %s")
            params.append(end_date)
        if food_name is not None:
            clauses.append("i.name ILIKE %s")
            params.append(f"%{food_name}%")
        if place is not None:
            clauses.append("r.place ILIKE %s")
            params.append(f"%{place}%")
        return " AND ".join(clauses), params

    @staticmethod
    def _hydrate_many(conn: Connection, rows: list[tuple]) -> list[Receipt]:
        if not rows:
            return []

        receipt_ids = [row[0] for row in rows]
        item_rows = conn.execute(
            """
            SELECT receipt_id, id, name, price, quantity
            FROM receipt_items WHERE receipt_id = ANY(%s) ORDER BY id
            """,
            (receipt_ids,),
        ).fetchall()

        items_by_receipt: dict[int, list[Item]] = {}
        for receipt_id, item_id, name, price, quantity in item_rows:
            items_by_receipt.setdefault(receipt_id, []).append(
                Item(id=item_id, name=name, price=float(price), quantity=quantity)
            )

        return [
            Receipt(
                id=receipt_id,
                place=place,
                uploaded_at=uploaded_at,
                transaction_date=transaction_date,
                total=float(total),
                image_path=image_path,
                items=items_by_receipt.get(receipt_id, []),
            )
            for receipt_id, place, uploaded_at, transaction_date, total, image_path in rows
        ]
