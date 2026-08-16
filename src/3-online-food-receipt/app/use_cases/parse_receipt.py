import base64
import logging

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage

from app.domain.entities import ParsedReceipt
from app.domain.exceptions import ReceiptParsingError
from app.use_cases import UseCaseBase

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = (
    "You are extracting structured data from a photo of a food purchase receipt. "
    "Read the merchant/place name, the transaction date printed on the receipt (if any), "
    "the grand total, and every purchased line item with its name, unit price, and quantity. "
    "If the transaction date truly cannot be determined, leave it null rather than guessing."
)


class ParseReceipt(UseCaseBase[bytes, ParsedReceipt]):
    def __init__(self, vision_model: BaseChatModel):
        self._model = vision_model.with_structured_output(ParsedReceipt)

    def execute(self, data: bytes) -> ParsedReceipt:
        image_b64 = base64.b64encode(data).decode("utf-8")
        message = HumanMessage(
            content=[
                {"type": "text", "text": EXTRACTION_PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            ]
        )

        try:
            result = self._model.invoke([message])
        except Exception as exc:  # noqa: BLE001 - surface any provider failure as a domain error
            logger.exception("Failed to parse receipt image")
            raise ReceiptParsingError(str(exc)) from exc

        if not isinstance(result, ParsedReceipt):
            raise ReceiptParsingError("Model did not return a structured receipt")

        return result
