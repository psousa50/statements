from datetime import date, datetime

import numpy as np
import pandas as pd

from src.app.services.file_processing.conversion_model import ConversionModel


class TransactionsCleaner:
    def clean(
        self, df: pd.DataFrame, conversion_model: ConversionModel
    ) -> pd.DataFrame:
        header_row = conversion_model.header_row
        start_row = conversion_model.start_row

        result_df = df.copy()

        if header_row > 0:
            column_names = result_df.iloc[header_row - 1].to_list()
            result_df.columns = column_names
            result_df = result_df.iloc[start_row - 1 :]
        else:
            column_names = result_df.iloc[header_row].to_list()
            result_df = result_df.iloc[start_row - 1 :]

        column_map = conversion_model.column_map

        rename_dict = {
            col: std_col
            for std_col, col in column_map.items()
            if col and col in result_df.columns
        }
        result_df = result_df.rename(columns=rename_dict)

        result_df = self._combine_debit_credit(result_df, conversion_model)

        for std_col in ["date", "description", "amount", "currency", "balance"]:
            if std_col not in result_df.columns:
                result_df[std_col] = "" if std_col == "currency" else np.nan

        if "date" in result_df.columns:
            result_df["date"] = self._parse_dates(result_df["date"])

        if "amount" in result_df.columns:
            result_df["amount"] = self._normalize_amount_column(result_df["amount"])

        if "balance" in result_df.columns:
            result_df["balance"] = self._normalize_amount_column(
                result_df["balance"], na_value=np.nan
            )

        return result_df

    def _combine_debit_credit(
        self, df: pd.DataFrame, conversion_model: ConversionModel
    ) -> pd.DataFrame:
        column_map = conversion_model.column_map
        if "amount" in column_map and column_map["amount"] != "":
            return df

        debit_col = "debit_amount"
        credit_col = "credit_amount"
        result_df = df.copy()
        if debit_col in result_df.columns:
            result_df[debit_col] = (
                result_df[debit_col].astype(str).str.replace(",", "", regex=False)
            )
            result_df[debit_col] = pd.to_numeric(
                result_df[debit_col], errors="coerce"
            ).fillna(0.0)
        if credit_col in result_df.columns:
            result_df[credit_col] = (
                result_df[credit_col].astype(str).str.replace(",", "", regex=False)
            )
            result_df[credit_col] = pd.to_numeric(
                result_df[credit_col], errors="coerce"
            ).fillna(0.0)
        result_df["amount"] = 0.0
        credit_mask = ~result_df[credit_col].isna() & (result_df[credit_col] != 0)
        result_df.loc[credit_mask, "amount"] = result_df.loc[credit_mask, credit_col]
        debit_mask = ~result_df[debit_col].isna() & (result_df[debit_col] != 0)
        result_df.loc[debit_mask, "amount"] = -result_df.loc[debit_mask, debit_col]
        result_df = result_df.drop(columns=[debit_col, credit_col])
        return result_df

    def _normalize_amount_column(
        self, amount_series: pd.Series, na_value: float = 0.0
    ) -> pd.Series:
        def normalize(val):
            if pd.isna(val):
                return na_value
            s = str(val).replace(",", "").strip()
            if s in {"", "00.00", "0.00", "0", "00"}:
                return 0.0
            if s.startswith("-"):
                try:
                    return -float(s[1:])
                except Exception:
                    return float("nan")
            try:
                return float(s)
            except Exception:
                return float("nan")

        return amount_series.apply(normalize)

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
            "%d-%b-%Y",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d-%m-%Y %H:%M:%S",
            "%Y.%m.%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%m.%d.%Y %H:%M:%S",
            "%m-%d-%Y %H:%M:%S",
            "%d %B %Y %H:%M:%S",
            "%b %d, %Y %H:%M:%S",
            "%B %d, %Y %H:%M:%S",
            "%d-%b-%Y %H:%M:%S",
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
