# Use existing transactions to categorize new transactions

When categorizing a new transaction:
- look for existing transactions with the same normalized description (distinct normalized description over the last 100 transactions)
- if the new transaction has the same normalized description, use the category of the existing transaction
- else fallback to an injected TransactionCategorizer


