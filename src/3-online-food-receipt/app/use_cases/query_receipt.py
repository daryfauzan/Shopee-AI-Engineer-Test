from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from app.agent.runner import AgentRunner
from app.agent.state import State
from app.domain.entities import Receipt
from app.domain.exceptions import ReceiptNotFoundError
from app.domain.repositories import ReceiptRepository
from app.use_cases import UseCaseBase


class ListReceipts(UseCaseBase[None, list[Receipt]]):
    def __init__(self, repository: ReceiptRepository):
        self._repository = repository

    def execute(self, data: None = None) -> list[Receipt]:
        return self._repository.list_all()


class GetReceipt(UseCaseBase[int, Receipt]):
    def __init__(self, repository: ReceiptRepository):
        self._repository = repository

    def execute(self, data: int) -> Receipt:
        receipt = self._repository.get_by_id(data)
        if receipt is None:
            raise ReceiptNotFoundError(f"Receipt {data} not found")
        return receipt


@dataclass
class SearchReceiptsInput:
    start_date: date | None = None
    end_date: date | None = None
    food_name: str | None = None
    place: str | None = None


class SearchReceipts(UseCaseBase[SearchReceiptsInput, list[Receipt]]):
    def __init__(self, repository: ReceiptRepository):
        self._repository = repository

    def execute(self, data: SearchReceiptsInput) -> list[Receipt]:
        return self._repository.search(
            start_date=data.start_date,
            end_date=data.end_date,
            food_name=data.food_name,
            place=data.place,
        )


class SumExpenses(UseCaseBase[SearchReceiptsInput, float]):
    def __init__(self, repository: ReceiptRepository):
        self._repository = repository

    def execute(self, data: SearchReceiptsInput) -> float:
        return self._repository.total_amount(
            start_date=data.start_date,
            end_date=data.end_date,
            food_name=data.food_name,
            place=data.place,
        )


@dataclass
class AskQuestionInput:
    question: str
    history: list[BaseMessage] = field(default_factory=list)


NO_ANSWER = "I couldn't come up with an answer. Please try rephrasing your question."


class AskQuestion(UseCaseBase[AskQuestionInput, str]):
    """Answers a natural-language question about the user's receipts via the LangGraph agent."""

    def __init__(self, runner: AgentRunner):
        self._runner = runner

    def execute(self, data: AskQuestionInput) -> str:
        state = State(messages=[*data.history, HumanMessage(content=data.question)])
        result = self._runner.run(state)

        for message in reversed(result.messages):
            if isinstance(message, AIMessage) and message.text:
                return str(message.text)

        return NO_ANSWER

    def stream(self, data: AskQuestionInput) -> Iterator[str]:
        """Yields the answer as it's generated, for incremental rendering (e.g. st.write_stream)."""
        state = State(messages=[*data.history, HumanMessage(content=data.question)])
        streamed = False
        for piece in self._runner.stream(state):
            streamed = True
            yield piece

        if not streamed:
            yield NO_ANSWER
