import json
from dataclasses import dataclass
from typing import List
from src.app.services.categorizers.transaction_categorizer import CategorizableTransaction
from src.app.models import Category

@dataclass
class Subcategory:
    category_id: int
    category_name: str
    subcategory_name: str


def categorization_prompt(transactions: List[CategorizableTransaction], categories: List[Category]) -> str:
    expanded_categories = [
        Subcategory(sub_cat.id, cat.category_name, sub_cat.category_name)
        for cat in categories
        if cat.subcategories is not None
        for sub_cat in cat.subcategories
    ]

    categories_info = [
        f"{{id: {cat.category_id}, name: {cat.subcategory_name}}}" for cat in expanded_categories
    ]

    transaction_descriptions = [
        f"{{transaction_id: {t.id}, description: {t.description}, normalized_description: {t.normalized_description}}}" for t in transactions
    ]

    prompt = f"""
You are a bank transaction categorization assistant. Your task is to categorize the following transaction description into one of the provided categories.

Transactions: 
{'\n'.join(transaction_descriptions)}

Available Categories:
{json.dumps(categories_info, indent=2)}

Analyze the transaction description and determine the most appropriate category ID from the list above.
Return your answer as a JSON object with the following format:
[
    {{
        "transaction_id": <id of the transaction>,
        "category_id": <id of the selected category or subcategory>,
        "confidence": <a number between 0 and 1 indicating your confidence in this categorization>
    }},
    {{
        "transaction_id": <id of the transaction>,
        "category_id": <id of the selected category or subcategory>,
        "confidence": <a number between 0 and 1 indicating your confidence in this categorization>
    }}
]

Only return the JSON object, nothing else.
"""
    return prompt
