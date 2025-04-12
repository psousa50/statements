import pandas as pd
from datetime import date

from src.app.services.file_processing.transactions_builder import TransactionsBuilder
from src.app.services.file_processing.transactions_builder import StatementTransaction


class TestTransactionsBuilder:
    def test_build_transactions(self):
        data = {
            "date": ["2023-01-17", "2023-01-15", "2023-01-20"],
            "description": ["Salary", "Groceries", "Housing"],
            "amount": [1000.00, -50.00, -100.00],
            "currency": ["EUR", "EUR", "EUR"],
        }
        df = pd.DataFrame(data)

        transactionsBuilder = TransactionsBuilder()
        transactions = transactionsBuilder.build_transactions(df)

        assert len(transactions) == 3
        assert transactions[0] == StatementTransaction(
            date=date(2023, 1, 17),
            description="Salary",
            amount=1000.00,
            currency="EUR",
        )
