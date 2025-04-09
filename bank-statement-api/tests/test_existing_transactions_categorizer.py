import pytest
from unittest.mock import MagicMock, AsyncMock
from decimal import Decimal
from datetime import date

from src.app.services.categorizers.transaction_categorizer import (
    CategorizableTransaction,
    CategorizationResult,
    TransactionCategorizer,
)
from src.app.repositories.transactions_repository import TransactionsRepository
from src.app.models import Transaction


class TestExistingTransactionsCategorizer:
    
    @pytest.fixture
    def transactions_repository(self):
        repo = MagicMock(spec=TransactionsRepository)
        
        # Sample transactions with the same normalized description but different categories
        existing_transactions = [
            Transaction(
                id=1,
                date=date.today(),
                description="COFFEE SHOP PAYMENT",
                normalized_description="coffee shop payment",
                amount=Decimal("4.50"),
                currency="EUR",
                category_id=5,  # Coffee shop category
                categorization_status="categorized"
            ),
            Transaction(
                id=2,
                date=date.today(),
                description="GROCERY STORE PURCHASE",
                normalized_description="grocery store purchase",
                amount=Decimal("45.67"),
                currency="EUR",
                category_id=3,  # Groceries category
                categorization_status="categorized"
            ),
            Transaction(
                id=3,
                date=date.today(),
                description="RESTAURANT DINNER",
                normalized_description="restaurant dinner",
                amount=Decimal("78.90"),
                currency="EUR",
                category_id=2,  # Restaurant category
                categorization_status="categorized"
            )
        ]
        
        # Mock the method to get transactions by normalized description
        def get_transactions_by_normalized_description_side_effect(normalized_description, limit):
            return [t for t in existing_transactions if t.normalized_description == normalized_description][:limit]
        
        repo.get_transactions_by_normalized_description = MagicMock(
            side_effect=get_transactions_by_normalized_description_side_effect
        )
        
        return repo
    
    @pytest.fixture
    def fallback_categorizer(self):
        categorizer = AsyncMock(spec=TransactionCategorizer)
        
        # Mock the categorize_transaction method to return predefined results
        async def categorize_transaction_side_effect(transactions):
            results = []
            for transaction in transactions:
                # Fallback categorizer assigns category 1 to all transactions
                results.append(
                    CategorizationResult(
                        id=transaction.id,
                        category_id=1,  # Default category
                        confidence=0.7
                    )
                )
            return results
        
        categorizer.categorize_transaction.side_effect = categorize_transaction_side_effect
        return categorizer
    
    @pytest.mark.asyncio
    async def test_categorize_transaction_with_existing_match(self, transactions_repository, fallback_categorizer):
        """Test that transactions with matching normalized descriptions get categorized based on existing transactions."""
        from src.app.services.categorizers.existing_transactions_categorizer import ExistingTransactionsCategorizer
        
        categorizer = ExistingTransactionsCategorizer(
            transactions_repository=transactions_repository,
            fallback_categorizer=fallback_categorizer
        )
        
        # Transaction with a normalized description that matches an existing one
        transactions = [
            CategorizableTransaction(
                id=101,
                description="Coffee Shop Payment",
                normalized_description="coffee shop payment"
            )
        ]
        
        results = await categorizer.categorize_transaction(transactions)
        
        # Should use the category from the existing transaction
        assert results[0].id == 101
        assert results[0].category_id == 5  # Coffee shop category
        assert results[0].confidence == 1.0  # High confidence for exact match
        
        # Verify the repository was called with the correct parameters
        transactions_repository.get_transactions_by_normalized_description.assert_called_once_with(
            "coffee shop payment", 100
        )
        
        # Verify the fallback categorizer was not called
        fallback_categorizer.categorize_transaction.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_categorize_transaction_without_existing_match(self, transactions_repository, fallback_categorizer):
        """Test that transactions without matching normalized descriptions use the fallback categorizer."""
        from src.app.services.categorizers.existing_transactions_categorizer import ExistingTransactionsCategorizer
        
        categorizer = ExistingTransactionsCategorizer(
            transactions_repository=transactions_repository,
            fallback_categorizer=fallback_categorizer
        )
        
        # Transaction with a normalized description that doesn't match any existing one
        transactions = [
            CategorizableTransaction(
                id=102,
                description="Online Subscription",
                normalized_description="online subscription"
            )
        ]
        
        results = await categorizer.categorize_transaction(transactions)
        
        # Should use the fallback categorizer
        assert results[0].id == 102
        assert results[0].category_id == 1  # Default category from fallback
        assert results[0].confidence == 0.7  # Confidence from fallback
        
        # Verify the repository was called with the correct parameters
        transactions_repository.get_transactions_by_normalized_description.assert_called_once_with(
            "online subscription", 100
        )
        
        # Verify the fallback categorizer was called with the correct parameters
        fallback_categorizer.categorize_transaction.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_categorize_multiple_transactions(self, transactions_repository, fallback_categorizer):
        """Test categorizing multiple transactions at once, some with matches and some without."""
        from src.app.services.categorizers.existing_transactions_categorizer import ExistingTransactionsCategorizer
        
        categorizer = ExistingTransactionsCategorizer(
            transactions_repository=transactions_repository,
            fallback_categorizer=fallback_categorizer
        )
        
        # Mix of transactions with and without matching normalized descriptions
        transactions = [
            CategorizableTransaction(
                id=103,
                description="Coffee Shop Payment",
                normalized_description="coffee shop payment"
            ),
            CategorizableTransaction(
                id=104,
                description="Online Subscription",
                normalized_description="online subscription"
            ),
            CategorizableTransaction(
                id=105,
                description="Restaurant Dinner",
                normalized_description="restaurant dinner"
            )
        ]
        
        results = await categorizer.categorize_transaction(transactions)
        
        # First transaction should match existing coffee shop
        assert results[0].id == 103
        assert results[0].category_id == 5
        assert results[0].confidence == 1.0
        
        # Second transaction should use fallback
        assert results[1].id == 104
        assert results[1].category_id == 1
        assert results[1].confidence == 0.7
        
        # Third transaction should match existing restaurant
        assert results[2].id == 105
        assert results[2].category_id == 2
        assert results[2].confidence == 1.0
        
        # Verify the repository was called for each transaction
        assert transactions_repository.get_transactions_by_normalized_description.call_count == 3
        
        # Verify the fallback categorizer was called only for the non-matching transaction
        fallback_categorizer.categorize_transaction.assert_called_once()
        # Check that only the non-matching transaction was passed to the fallback
        assert len(fallback_categorizer.categorize_transaction.call_args[0][0]) == 1
        assert fallback_categorizer.categorize_transaction.call_args[0][0][0].id == 104
    
    @pytest.mark.asyncio
    async def test_refresh_rules(self, transactions_repository, fallback_categorizer):
        """Test that refresh_rules passes through to the fallback categorizer."""
        from src.app.services.categorizers.existing_transactions_categorizer import ExistingTransactionsCategorizer
        
        categorizer = ExistingTransactionsCategorizer(
            transactions_repository=transactions_repository,
            fallback_categorizer=fallback_categorizer
        )
        
        # Mock return value for the fallback categorizer's refresh_rules method
        fallback_categorizer.refresh_rules.return_value = ["rule1", "rule2"]
        
        result = categorizer.refresh_rules()
        
        # Should pass through to the fallback categorizer
        fallback_categorizer.refresh_rules.assert_called_once()
        assert result == ["rule1", "rule2"]
