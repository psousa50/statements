Delay categorization on transactions

When transaction is created:
- tx should be marked and saved as not categorized. There should be a status column for that and the category could be set to null
- There should be an independent categorization process that can be triggered manuallym automatically (every x minutes), or by code, (Use Celery for that, unless you think there are other better options)

When categorization is triggered:
- a batch of non categorized transactions should be fetched
- the TransactionCategorizer should be used to categorize the transactions
- the categorization process should update the transaction with the new category and status
