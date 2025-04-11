from datetime import date, datetime

import numpy as np
import pandas as pd

from src.app.services.file_processing.conversion_model import ConversionModel


class TransactionCleaner:
    def __init__(self, conversion_model: ConversionModel):
        self.conversion_model = conversion_model

    def clean(self, df: pd.DataFrame) -> (pd.DataFrame, list[str]):
        header_row = self.conversion_model.header_row
        start_row = self.conversion_model.start_row

        result_df = df.copy()

        column_names = result_df.iloc[header_row].to_list()
        if header_row > 0:
            result_df = result_df.iloc[start_row:]
        else:
            result_df = result_df.iloc[start_row - 1 :]

        result_df = self._combine_debit_credit(result_df)

        for std_col in ["date", "description", "amount", "currency", "balance"]:
            if std_col not in result_df.columns:
                result_df[std_col] = "" if std_col == "currency" else np.nan

        if "date" in result_df.columns:
            result_df["date"] = self._parse_dates(result_df["date"])

        if "amount" in result_df.columns:
            result_df["amount"] = pd.to_numeric(result_df["amount"], errors="coerce")

        if "balance" in result_df.columns:
            result_df["balance"] = pd.to_numeric(result_df["balance"], errors="coerce")

        return result_df, column_names

    def _combine_debit_credit(self, df: pd.DataFrame) -> pd.DataFrame:
        column_map = self.conversion_model.column_map
        if "amount" not in column_map or column_map["amount"] != "":
            return df

        debit_col = "debit_amount"
        credit_col = "credit_amount"

        result_df = df.copy()

        result_df["amount"] = 0.0

        credit_mask = ~result_df[credit_col].isna() & (result_df[credit_col] != 0)
        result_df.loc[credit_mask, "amount"] = result_df.loc[credit_mask, credit_col]

        debit_mask = ~result_df[debit_col].isna() & (result_df[debit_col] != 0)
        result_df.loc[debit_mask, "amount"] = -result_df.loc[debit_mask, debit_col]

        result_df = result_df.drop(columns=[debit_col, credit_col])

        return result_df

    def _parse_dates(self, date_series: pd.Series) -> pd.Series:
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%Y.%m.%d",
            "%d.%m.%Y",
            "%Y/%m/%d",
            "%d %b %Y",
            "%d %B %Y",
            "%b %d, %Y",
            "%B %d, %Y",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d-%m-%Y %H:%M:%S",
            "%Y.%m.%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%m.%d.%Y",
            "%m-%d-%Y",
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
