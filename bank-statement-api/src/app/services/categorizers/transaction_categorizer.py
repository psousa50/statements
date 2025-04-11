from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CategorisationData:
    transaction_id: int
    description: str
    normalized_description: str


@dataclass
class CategorizationResult:
    transaction_id: int
    sub_category_id: Optional[int]
    confidence: float


class TransactionCategorizer(ABC):
    @abstractmethod
    async def categorize_transaction(
        self, transactions: List[CategorisationData]
    ) -> List[CategorizationResult]:
        pass

    @abstractmethod
    def refresh_rules(self):
        pass
