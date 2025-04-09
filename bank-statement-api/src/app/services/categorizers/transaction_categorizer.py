from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class CategorizableTransaction:
    id: int
    description: str
    normalized_description: str


@dataclass
class CategorizationResult:
    id: int
    category_id: Optional[int]
    confidence: float


class TransactionCategorizer(ABC):
    @abstractmethod
    async def categorize_transaction(self, transactions: List[CategorizableTransaction]) -> List[CategorizationResult]:
        pass

    @abstractmethod
    def refresh_rules(self):
        pass
