from typing import Dict, List, Optional
from datetime import datetime, date
import pandas as pd
import numpy as np
import re


class TransactionCleaner:
    def clean(self, df: pd.DataFrame, column_map: Dict[str, str]) -> pd.DataFrame:
        """
        Clean and normalize a transaction dataframe.
        
        Args:
            df: Original DataFrame with transaction data
            column_map: Mapping of original column names to standard column names
            
        Returns:
            Cleaned DataFrame with standardized columns and values
        """
        # Create a copy to avoid modifying the original
        result_df = df.copy()
        
        # Create a reverse mapping (standard_name -> original_name)
        reverse_map = self._create_reverse_map(column_map)
        
        # Handle separate debit and credit columns if they exist
        result_df = self._combine_debit_credit(result_df, column_map)
        
        # Rename columns based on the column map
        rename_dict = {col: std_col for col, std_col in column_map.items() 
                      if std_col and col in df.columns}
        result_df = result_df.rename(columns=rename_dict)
        
        # Add missing standard columns with default values
        for std_col in ["date", "description", "amount", "currency", "balance"]:
            if std_col not in result_df.columns:
                result_df[std_col] = "" if std_col == "currency" else np.nan
        
        # Apply transformations to specific columns
        if "date" in result_df.columns:
            result_df["date"] = self._parse_dates(result_df["date"])
            
        if "amount" in result_df.columns:
            result_df["amount"] = pd.to_numeric(result_df["amount"], errors="coerce")
            
        if "balance" in result_df.columns:
            result_df["balance"] = pd.to_numeric(result_df["balance"], errors="coerce")
            
        return result_df
    
    def _create_reverse_map(self, column_map: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Create a reverse mapping from standard column names to original column names.
        
        Args:
            column_map: Mapping of original column names to standard column names
            
        Returns:
            Dictionary mapping standard column names to lists of original column names
        """
        reverse_map = {}
        for orig_col, std_col in column_map.items():
            if std_col:  # Skip empty strings
                if std_col not in reverse_map:
                    reverse_map[std_col] = []
                reverse_map[std_col].append(orig_col)
        return reverse_map
    
    def _combine_debit_credit(self, df: pd.DataFrame, column_map: Dict[str, str]) -> pd.DataFrame:
        """
        Combine separate debit and credit columns into a single amount column.
        
        Args:
            df: Original DataFrame
            column_map: Column mapping from normalize_columns
            
        Returns:
            DataFrame with combined amount column if applicable
        """
        # Find columns mapped to "amount"
        amount_columns = [col for col, std_col in column_map.items() 
                         if std_col == "amount" and col in df.columns]
        
        if len(amount_columns) <= 1:
            return df  # No need to combine
        
        # Check if we have debit and credit columns
        debit_patterns = ["debit", "withdrawal", "payments", "out"]
        credit_patterns = ["credit", "deposit", "incoming", "in"]
        
        debit_col = None
        credit_col = None
        
        for col in amount_columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in debit_patterns):
                debit_col = col
            elif any(pattern in col_lower for pattern in credit_patterns):
                credit_col = col
        
        if debit_col and credit_col:
            # Create a copy to avoid modifying the original
            result_df = df.copy()
            
            # Create a new amount column
            result_df["amount"] = 0.0
            
            # Fill with credit values (positive)
            credit_mask = ~result_df[credit_col].isna() & (result_df[credit_col] != 0)
            result_df.loc[credit_mask, "amount"] = result_df.loc[credit_mask, credit_col]
            
            # Fill with debit values (negative)
            debit_mask = ~result_df[debit_col].isna() & (result_df[debit_col] != 0)
            result_df.loc[debit_mask, "amount"] = -result_df.loc[debit_mask, debit_col]
            
            # Drop the original debit and credit columns
            result_df = result_df.drop(columns=[debit_col, credit_col])
            
            return result_df
        
        return df
    
    def _parse_dates(self, date_series: pd.Series) -> pd.Series:
        """
        Parse dates in various formats to datetime objects.
        
        Args:
            date_series: Series containing date strings
            
        Returns:
            Series with parsed dates
        """
        # Try multiple date formats
        date_formats = [
            "%Y-%m-%d",      # 2023-01-01
            "%d/%m/%Y",      # 01/01/2023
            "%m/%d/%Y",      # 01/01/2023 (US format)
            "%d-%m-%Y",      # 01-01-2023
            "%Y.%m.%d",      # 2023.01.01
            "%d.%m.%Y",      # 01.01.2023
            "%Y/%m/%d",      # 2023/01/01
            "%d %b %Y",      # 01 Jan 2023
            "%d %B %Y",      # 01 January 2023
            "%b %d, %Y",     # Jan 01, 2023
            "%B %d, %Y",     # January 01, 2023
        ]
        
        def parse_date(date_str):
            if pd.isna(date_str):
                return pd.NaT
            
            if isinstance(date_str, (datetime, date)):
                return date_str
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(str(date_str).strip(), fmt).date()
                except ValueError:
                    continue
            
            return pd.NaT
        
        return date_series.apply(parse_date)
    
    def _normalize_descriptions(self, desc_series: pd.Series) -> pd.Series:
        """
        Normalize transaction descriptions.
        
        Args:
            desc_series: Series containing transaction descriptions
            
        Returns:
            Series with normalized descriptions
        """
