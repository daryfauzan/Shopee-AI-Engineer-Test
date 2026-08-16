from dataclasses import dataclass

from app.adapters import LocalReceiptImageStore
from app.domain.entities import ParsedReceipt, Receipt
from app.domain.repositories import ReceiptRepository
from app.use_cases import UseCaseBase


@dataclass
class LoadReceiptInput:
    parsed: ParsedReceipt
    image_bytes: bytes
    image_filename: str


class LoadReceipt(UseCaseBase[LoadReceiptInput, Receipt]):
    """Persists a (possibly user-corrected) parsed receipt together with its source image."""

    def __init__(self, repository: ReceiptRepository, image_store: LocalReceiptImageStore):
        self._repository = repository
        self._image_store = image_store

    def execute(self, data: LoadReceiptInput) -> Receipt:
        image_path = self._image_store.save(data.image_bytes, data.image_filename)
        return self._repository.save(data.parsed, image_path)
