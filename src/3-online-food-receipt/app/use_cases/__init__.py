from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class UseCaseBase(ABC, Generic[TInput, TOutput]):
    @abstractmethod
    def execute(self, data: TInput) -> TOutput: ...
