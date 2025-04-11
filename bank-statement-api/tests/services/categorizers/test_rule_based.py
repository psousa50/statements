from unittest.mock import MagicMock

import pytest

from src.app.services.categorizers.rule_based import RuleBasedTransactionCategorizer
from src.app.services.categorizers.transaction_categorizer import CategorisationData
from tests.conftest import create_category_tree


@pytest.mark.asyncio
async def test_rule_based_categorizer():
    categories = create_category_tree(
        id=10,
        category_name="Food",
        subcategory_id_1=20,
        subcategory_name_1="Restaurant",
        subcategory_id_2=30,
        subcategory_name_2="Groceries",
    )
    categories_repository = MagicMock()
    categories_repository.get_all.return_value = categories

    categorizer = RuleBasedTransactionCategorizer(
        categories_repository=categories_repository
    )

    transactions = [
        CategorisationData(
            transaction_id=100,
            description="Payment to GROCERIES STORE",
            normalized_description="Payment to GROCERIES STORE",
        )
    ]
    results = await categorizer.categorize_transaction(transactions)

    assert results[0].transaction_id == 100
    assert results[0].sub_category_id == 30
    assert results[0].confidence == 1.0
