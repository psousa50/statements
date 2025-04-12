from datetime import date

from src.app.services.file_processing.statement_statistics_calculator import (
    StatementStatisticsCalculator,
)
from src.app.services.file_processing.transactions_builder import StatementTransaction


class TestStatementStatisticsCalculator:
    def test_calc_statistics(self):
        transactions = [
            StatementTransaction(
                date=date(2023, 1, 17),
                description="Salary",
                amount=1000.00,
                currency="EUR",
            ),
            StatementTransaction(
                date=date(2023, 1, 15),
                description="Groceries",
                amount=-50.00,
                currency="EUR",
            ),
            StatementTransaction(
                date=date(2023, 1, 20),
                description="Housing",
                amount=-100.00,
                currency="EUR",
            ),
        ]

        statementStatistics = StatementStatisticsCalculator()
        statistics = statementStatistics.calc_statistics(transactions)

        assert statistics.total_transactions == 3
        assert statistics.total_amount == 850.00
        assert statistics.date_range_start == date(2023, 1, 15)
        assert statistics.date_range_end == date(2023, 1, 20)
