from typing import Dict, Set

import pandas as pd


class ColumnNormalizer:
    def __init__(self):
        self.standard_columns = ["date", "description", "amount", "currency", "balance"]
        
        # Define possible column name variations for each standard column
        self.column_variations = {
            "date": [
                "date", "transaction date", "trans date", "posting date", "value date"
            ],
            "description": [
                "description", "transaction details", "details", "narrative", "particulars", 
                "transaction", "transaction description", "memo"
            ],
            "amount": [
                "amount", "debit/credit", "value", "transaction amount", "sum",
                "debit", "credit", "deposit", "withdrawal"
            ],
            "currency": [
                "currency", "curr", "curr.", "ccy"
            ],
            "balance": [
                "balance", "available balance", "running balance", "closing balance", 
                "end balance", "account balance"
            ]
        }

    def normalize_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Map dataframe column names to standard column names.
        
        Args:
            df: DataFrame with columns to normalize
            
        Returns:
            Dictionary mapping original column names to standard column names.
            If a standard column doesn't exist, it will map to an empty string.
        """
        column_map = {}
        df_columns_lower = {col.lower(): col for col in df.columns}
        
        # First try exact matches (case-insensitive)
        for std_col in self.standard_columns:
            if std_col in df_columns_lower:
                column_map[df_columns_lower[std_col]] = std_col
        
        # Then try variations
        for std_col, variations in self.column_variations.items():
            for var in variations:
                if var in df_columns_lower and df_columns_lower[var] not in column_map:
                    column_map[df_columns_lower[var]] = std_col
        
        # Add empty strings for missing standard columns
        mapped_std_cols = set(column_map.values())
        for std_col in self.standard_columns:
            if std_col not in mapped_std_cols:
                column_map[std_col] = ""
                    
        return column_map
