from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from src.app.services.file_processing.transactions_builder import StatementTransaction


@dataclass
class StatementStatistics:
    total_transactions: int
    total_amount: float
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None


class StatementStatisticsCalculator:

    def calc_statistics(
        self, transactions: List[StatementTransaction]
    ) -> StatementStatistics:
        total_transactions = len(transactions)
        total_amount = sum(transaction.amount for transaction in transactions)
        date_range_start = min(transaction.date for transaction in transactions)
        date_range_end = max(transaction.date for transaction in transactions)
        return StatementStatistics(
            total_transactions, total_amount, date_range_start, date_range_end
        )
