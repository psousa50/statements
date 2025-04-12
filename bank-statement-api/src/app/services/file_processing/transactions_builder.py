from datetime import date
from decimal import Decimal
from typing import List

import pandas as pd
from pydantic import BaseModel


class StatementTransaction(BaseModel):
    date: date
    description: str
    amount: Decimal
    currency: str


class TransactionsBuilder:

    def build_transactions(self, df: pd.DataFrame) -> List[StatementTransaction]:
        df["amount"] = df["amount"].apply(lambda x: Decimal(str(x)))
        return [
            StatementTransaction(
                date=row.date,
                description=row.description,
                amount=row.amount,
                currency=row.currency,
            )
            for row in df.itertuples(index=False)
        ]
