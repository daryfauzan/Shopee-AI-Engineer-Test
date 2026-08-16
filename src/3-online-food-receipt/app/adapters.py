import logging
from pathlib import Path
from uuid import uuid4

from langchain_openai import ChatOpenAI
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS receipts (
        id SERIAL PRIMARY KEY,
        place TEXT NOT NULL,
        uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        transaction_date DATE,
        total NUMERIC(12, 2) NOT NULL,
        image_path TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS receipt_items (
        id SERIAL PRIMARY KEY,
        receipt_id INTEGER NOT NULL REFERENCES receipts(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        price NUMERIC(12, 2) NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_receipt_items_name ON receipt_items (name)",
    "CREATE INDEX IF NOT EXISTS idx_receipts_transaction_date ON receipts (transaction_date)",
]


def build_connection_pool(dsn: str, min_size: int, max_size: int) -> ConnectionPool:
    return ConnectionPool(conninfo=dsn, min_size=min_size, max_size=max_size, open=True)


def init_schema(pool: ConnectionPool) -> None:
    with pool.connection() as conn:
        for statement in SCHEMA_STATEMENTS:
            conn.execute(statement)
    logger.info("Database schema ensured")


def build_chat_model(
    api_key: str, model_name: str, base_url: str | None = None
) -> ChatOpenAI:
    """A single multimodal OpenAI-compatible model, used both for receipt-image extraction and the Q&A agent."""
    return ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url, temperature=0)


class LocalReceiptImageStore:
    """Stores uploaded receipt images on local disk."""

    def __init__(self, base_dir: Path):
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, data: bytes, filename: str) -> str:
        suffix = Path(filename).suffix or ".jpg"
        stored_path = self._base_dir / f"{uuid4().hex}{suffix}"
        stored_path.write_bytes(data)
        return str(stored_path)

    def read(self, path: str) -> bytes:
        return Path(path).read_bytes()
