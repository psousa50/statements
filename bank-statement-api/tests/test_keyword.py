from unittest.mock import MagicMock

from src.app.services.categorizers.keyword import KeywordTransactionCategorizer
from src.app.services.categorizers.transaction_categorizer import CategorisationData
from tests.conftest import create_category_tree


def test_keyword_categorizer():
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

    categorizer = KeywordTransactionCategorizer(
        categories_repository=categories_repository
    )

    categorizer.add_keyword("grocery", 30)
    categorizer.add_keyword("restaurant", 20)

    transactions = [
        CategorisationData(
            transaction_id=100,
            description="Dinner at FANCY RESTAURANT",
            normalized_description="Dinner at FANCY RESTAURANT",
        ),
        CategorisationData(
            transaction_id=200,
            description="Payment to GROCERIES STORE",
            normalized_description="Payment to GROCERIES STORE",
        ),
    ]
    results = categorizer.categorize_transaction(transactions)

    assert results[0].transaction_id == 100
    assert results[0].category_id == 20
    assert results[0].confidence > 0.0

    assert results[1].transaction_id == 200
    assert results[1].category_id == 30
    assert results[1].confidence > 0.0

