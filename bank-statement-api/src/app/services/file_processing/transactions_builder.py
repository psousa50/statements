from decimal import Decimal
from typing import List

import pandas as pd

from src.app.schemas import StatementTransaction


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
