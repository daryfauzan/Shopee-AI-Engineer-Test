from abc import ABC, abstractmethod
from datetime import date

from .entities import ParsedReceipt, Receipt


class ReceiptRepository(ABC):
    @abstractmethod
    def save(self, parsed: ParsedReceipt, image_path: str) -> Receipt: ...

    @abstractmethod
    def get_by_id(self, receipt_id: int) -> Receipt | None: ...

    @abstractmethod
    def list_all(self) -> list[Receipt]: ...

    @abstractmethod
    def search(
        self,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        food_name: str | None = None,
        place: str | None = None,
    ) -> list[Receipt]: ...

    @abstractmethod
    def total_amount(
        self,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        food_name: str | None = None,
        place: str | None = None,
    ) -> float:
        """Sum of matching totals, computed deterministically in SQL (never by the LLM)."""
        ...
