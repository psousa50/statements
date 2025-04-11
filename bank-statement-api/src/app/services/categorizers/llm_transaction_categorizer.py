import logging
from dataclasses import dataclass
from typing import List

from src.app.ai.llm_client import LLMClient
from src.app.common.json_utils import sanitize_json
from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.prompts import categorization_prompt
from src.app.services.categorizers.transaction_categorizer import (
    CategorisationData,
    CategorizationResult,
    TransactionCategorizer,
)

logger_content = logging.getLogger("app.llm.big")


@dataclass
class Subcategory:
    category_id: int
    category_name: str
    subcategory_name: str


@dataclass
class LLMCategorizationResult:
    transaction_description: str
    sub_category_id: int
    confidence: float


class LLMTransactionCategorizer(TransactionCategorizer):
    def __init__(
        self, categories_repository: CategoriesRepository, llm_client: LLMClient
    ):
        self.categories_repository = categories_repository
        self.llm_client = llm_client
        self.categories = categories_repository.get_all()
        self.refresh_rules()

    async def categorize_transaction(
        self, transactions: List[CategorisationData]
    ) -> List[CategorizationResult]:
        if not self.categories:
            raise ValueError("Categories not loaded")

        prompt = categorization_prompt(transactions, self.categories)
        response = await self.llm_client.generate_async(prompt)
        logger_content.debug(
            "Raw Response: %s",
            response,
            extra={"prefix": "llm_transaction_categorizer"},
        )
        json_result = sanitize_json(response)
        if not json_result:
            raise ValueError("Invalid JSON response")
        llm_categorization_results = [
            LLMCategorizationResult(**result) for result in json_result
        ]
        categorized_results = []
        for llm_result in llm_categorization_results:
            transaction_description = llm_result.transaction_description
            sub_category_id = llm_result.sub_category_id
            confidence = llm_result.confidence
            for transaction in transactions:
                if transaction.normalized_description == transaction_description:
                    categorized_results.append(
                        CategorizationResult(
                            transaction_id=transaction.transaction_id,
                            sub_category_id=sub_category_id,
                            confidence=confidence,
                        )
                    )
        return categorized_results

    def refresh_rules(self):
        self.categories = self.categories_repository.get_all()
        return self.categories
