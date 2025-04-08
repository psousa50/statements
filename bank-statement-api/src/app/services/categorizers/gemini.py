import json
from typing import Optional, Tuple

from src.app.ai.gemini_pro import GeminiPro
from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.embedding import TransactionCategorizer


class GeminiTransactionCategorizer(TransactionCategorizer):
    def __init__(
        self,
        categories_repository: CategoriesRepository,
        api_key: Optional[str] = None,
        model_name: str = "gemini-pro",
    ):
        self.categories_repository = categories_repository
        self.gemini = GeminiPro(api_key=api_key, model_name=model_name)
        self.categories = []
        self.refresh_rules()

    async def categorize_transaction(self, description: str) -> Tuple[Optional[int], float]:
        if not self.categories:
            return None, 0.0

        try:
            prompt = self._create_categorization_prompt(description)
            response = await self.gemini.generate(prompt)
            
            # Parse the response to extract category_id and confidence
            try:
                result = json.loads(response)
                category_id = result.get("category_id")
                confidence = result.get("confidence", 0.0)
                
                if category_id is not None:
                    return int(category_id), float(confidence)
            except json.JSONDecodeError:
                # If response isn't valid JSON, try to extract just the category ID
                for category in self.categories:
                    if str(category.id) in response:
                        return category.id, 0.7
                        
            return None, 0.0
        except Exception:
            return None, 0.0

    def refresh_rules(self):
        self.categories = self.categories_repository.get_all()
        return self.categories
    
    def _create_categorization_prompt(self, description: str) -> str:
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

Transaction: "{description}"

Available Categories:
{json.dumps(categories_info, indent=2)}

Analyze the transaction description and determine the most appropriate category ID from the list above.
Return your answer as a JSON object with the following format:
{{
  "category_id": <id of the selected category or subcategory>,
  "confidence": <a number between 0 and 1 indicating your confidence in this categorization>
}}

Only return the JSON object, nothing else.
"""
        return prompt
