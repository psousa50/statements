import json
from dataclasses import dataclass
from typing import List

from src.app.models import Category
from src.app.services.categorizers.transaction_categorizer import (
    CategorisationData,
)


@dataclass
class Subcategory:
    sub_category_id: int
    subcategory_name: str


def categorization_prompt(
    transactions: List[CategorisationData], categories: List[Category]
) -> str:
    expanded_categories = [
        Subcategory(sub_cat.id, sub_cat.category_name)
        for cat in categories
        if cat.subcategories is not None
        for sub_cat in cat.subcategories
    ]

    categories_info = [
        f"{{id: {cat.sub_category_id}, name: {cat.subcategory_name}}}"
        for cat in expanded_categories
    ]

    transaction_descriptions = [t.normalized_description for t in transactions]

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
        "transaction_description": <description of the transaction>,
        "sub_category_id": <id of the selected subcategory>,
        "confidence": <a number between 0 and 1 indicating your confidence in this categorization>
    }},
    {{
        "transaction_description": <description of the transaction>,
        "sub_category_id": <id of the selected subcategory>,
        "confidence": <a number between 0 and 1 indicating your confidence in this categorization>
    }}
]

Only return the JSON object, nothing else.
"""
    return prompt
