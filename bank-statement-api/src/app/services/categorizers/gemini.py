from typing import List, Optional
import json

from src.app.ai.gemini_pro import GeminiPro
from src.app.services.categorizers.transaction_categorizer import CategorizableTransaction, CategorizationResult, TransactionCategorizer
from src.app.repositories.categories_repository import CategoriesRepository


class GeminiTransactionCategorizer(TransactionCategorizer):
    def __init__(
        self,
        categories_repository: CategoriesRepository,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-pro-exp-03-25",
    ):
        self.categories_repository = categories_repository
        self.gemini = GeminiPro(api_key=api_key, model_name=model_name)
        self.categories = categories_repository.get_all()
        self.refresh_rules()

    async def categorize_transaction(self, transactions: List[CategorizableTransaction]) -> List[CategorizationResult]:
        if not self.categories:
            raise ValueError("Categories not loaded")

        try:
            prompt = self._create_categorization_prompt(transactions)
            response = await self.gemini.generate(prompt)
            
            # Parse the response to extract category_id and confidence
            try:
                results = json.loads(response)
                categorized_results = []
                for i, result in enumerate(results):
                    category_id = result.get("category_id")
                    confidence = result.get("confidence", 0.0)
                    if category_id is not None:
                        categorized_results.append(CategorizationResult(id=transactions[i].id, category_id=category_id, confidence=confidence))
                return categorized_results
            except json.JSONDecodeError:
                # If response isn't valid JSON, try to extract just the category ID
                for category in self.categories:
                    if str(category.id) in response:
                        return [CategorizationResult(id=transaction.id, category_id=category.id, confidence=0.7) for transaction in transactions]
                
            except Exception as e:
                print(f"Error: {e}")
                raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e

    def refresh_rules(self):
        self.categories = self.categories_repository.get_all()
        return self.categories
    
    def _create_categorization_prompt(self, transactions: List[CategorizableTransaction]) -> str:
        categories_info = []
        
        for category in self.categories:
            category_info = {
                "id": category.id,
                "name": category.category_name,
            }
            
            if category.subcategories:
                subcategories = [
                    {"id": sub.id, "name": sub.category_name}
                    for sub in category.subcategories
                ]
                category_info["subcategories"] = subcategories
                
            categories_info.append(category_info)
            
        prompt = f"""
You are a bank transaction categorization assistant. Your task is to categorize the following transaction description into one of the provided categories.

Transactions: 
{json.dumps([t.normalized_description for t in transactions], indent=2)}


Available Categories:
{json.dumps(categories_info, indent=2)}

Analyze the transaction description and determine the most appropriate category ID from the list above.
Return your answer as a JSON object with the following format:
[
    {{
        "category_id": <id of the selected category or subcategory>,
        "confidence": <a number between 0 and 1 indicating your confidence in this categorization>
    }},
    {{
        "category_id": <id of the selected category or subcategory>,
        "confidence": <a number between 0 and 1 indicating your confidence in this categorization>
    }}
]

Only return the JSON object, nothing else.
"""
        print(prompt)
        return prompt
