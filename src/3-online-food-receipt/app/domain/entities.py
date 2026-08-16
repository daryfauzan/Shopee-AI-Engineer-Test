from datetime import date, datetime

from pydantic import BaseModel, Field


class Item(BaseModel):
    id: int | None = None
    name: str
    price: float
    quantity: int = 1


class ReceiptBase(BaseModel):
    place: str
    transaction_date: date | None
    total: float


class ParsedReceipt(ReceiptBase):
    """Structured data extracted from a receipt image, not yet persisted."""

    items: list[Item] = Field(default_factory=list)


class Receipt(ReceiptBase):
    id: int
    uploaded_at: datetime
    image_path: str
    items: list[Item] = Field(default_factory=list)
