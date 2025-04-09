from unittest.mock import AsyncMock, MagicMock
from collections import namedtuple

import pytest

from src.app.repositories.transactions_repository import TransactionsRepository
from src.app.services.categorizers.existing_transactions_categorizer import (
    ExistingTransactionsCategorizer,
)
from src.app.services.categorizers.transaction_categorizer import (
    CategorisationData,
    CategorizationResult,
    TransactionCategorizer,
)


class TestExistingTransactionsCategorizer:
    
    ExpectedCategorization = namedtuple('ExpectedCategorization', ['category_id', 'confidence'])
    
    @pytest.fixture
    def transactions_repository(self):
        repo = MagicMock(spec=TransactionsRepository)
        
        # Create a list of (normalized_description, category_id) tuples
        description_category_pairs = [
            ("coffee shop payment", 10),
            ("grocery store purchase", 20),
            ("restaurant dinner", 30),
        ]
        
        repo.get_unique_normalized_descriptions = MagicMock(
            return_value=description_category_pairs
        )
        
        return repo
    
    @pytest.fixture
    def fallback_categorizer(self):
        categorizer = AsyncMock(spec=TransactionCategorizer)
        
        async def categorize_transaction_side_effect(transactions):
            results = []
            for transaction in transactions:
                results.append(
                    CategorizationResult(
                        transaction_id=transaction.transaction_id,
                        category_id=1,
                        confidence=0.7
                    )
                )
            return results
        
        categorizer.categorize_transaction.side_effect = categorize_transaction_side_effect
        return categorizer
    
    @pytest.mark.asyncio
    async def test_categorize_transaction_with_existing_match(self, transactions_repository, fallback_categorizer):
        categorizer = ExistingTransactionsCategorizer(
            transactions_repository=transactions_repository,
            fallback_categorizer=fallback_categorizer
        )
        
        transactions = [
            CategorisationData(
                transaction_id=100,
                description="Coffee Shop Payment",
                normalized_description="coffee shop payment"
            )
        ]
        
        results = await categorizer.categorize_transaction(transactions)
        
        assert results[0].transaction_id == 100
        assert results[0].category_id == 10
        assert results[0].confidence == 1.0
        
        transactions_repository.get_unique_normalized_descriptions.assert_called_once_with(
            100
        )
        
        fallback_categorizer.categorize_transaction.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_categorize_transaction_without_existing_match(self, transactions_repository, fallback_categorizer):
        categorizer = ExistingTransactionsCategorizer(
            transactions_repository=transactions_repository,
            fallback_categorizer=fallback_categorizer
        )
        
        transactions = [
            CategorisationData(
                transaction_id=200,
                description="Online Subscription",
                normalized_description="online subscription"
            )
        ]
        
        results = await categorizer.categorize_transaction(transactions)
        
        assert results[0].transaction_id == 200
        assert results[0].category_id == 1
        assert results[0].confidence == 0.7
        
        transactions_repository.get_unique_normalized_descriptions.assert_called_once_with(
            100
        )
        
        fallback_categorizer.categorize_transaction.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_categorize_multiple_transactions(self, transactions_repository, fallback_categorizer):
        categorizer = ExistingTransactionsCategorizer(
            transactions_repository=transactions_repository,
            fallback_categorizer=fallback_categorizer
        )
        
        transactions = [
            CategorisationData(
                transaction_id=100,
                description="Coffee Shop Payment",
                normalized_description="coffee shop payment"
            ),
            CategorisationData(
                transaction_id=200,
                description="Online Subscription",
                normalized_description="online subscription"
            ),
            CategorisationData(
                transaction_id=300,
                description="Restaurant Dinner",
                normalized_description="restaurant dinner"
            )
        ]
        
        results = await categorizer.categorize_transaction(transactions)
        
        expected_results = {
            100: self.ExpectedCategorization(category_id=10, confidence=1.0),
            200: self.ExpectedCategorization(category_id=1, confidence=0.7),
            300: self.ExpectedCategorization(category_id=30, confidence=1.0),
        }
        
        assert len(results) == len(expected_results)
        
        for result in results:
            expected = expected_results[result.transaction_id]
            assert result.category_id == expected.category_id
            assert result.confidence == expected.confidence
        
        assert transactions_repository.get_unique_normalized_descriptions.call_count == 1
        
        fallback_categorizer.categorize_transaction.assert_called_once()
        assert len(fallback_categorizer.categorize_transaction.call_args[0][0]) == 1
        assert fallback_categorizer.categorize_transaction.call_args[0][0][0].normalized_description == "online subscription"
    
    @pytest.mark.asyncio
    async def test_refresh_rules(self, transactions_repository, fallback_categorizer):
        categorizer = ExistingTransactionsCategorizer(
            transactions_repository=transactions_repository,
            fallback_categorizer=fallback_categorizer
        )
        
        fallback_categorizer.refresh_rules.return_value = ["rule1", "rule2"]
        
        result = categorizer.refresh_rules()
        
        fallback_categorizer.refresh_rules.assert_called_once()
        assert result == ["rule1", "rule2"]
