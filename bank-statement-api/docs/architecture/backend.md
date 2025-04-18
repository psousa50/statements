# Bank Statement API Architecture

## Core Components

### Models
- `Transaction`: Represents a financial transaction with fields like date, description, amount, category_id, normalized_description, and categorization_status.
- `Category`: Represents a transaction category with id and name.
- `Source`: Represents a source of transactions (e.g., a bank).

### Repositories
- `TransactionsRepository`: Handles database operations for transactions, including querying, creating, updating, and filtering transactions.
- `CategoriesRepository`: Manages category data in the database.
- `SourcesRepository`: Manages source data in the database.

### Services
- `TransactionCategorizationService`: Coordinates the categorization of transactions by retrieving uncategorized transactions and using a categorizer to assign categories.

### Categorizers
- `TransactionCategorizer` (Abstract Base Class): Defines the interface for transaction categorizers with methods:
  - `categorize_transaction`: Takes a list of CategorizableTransaction objects and returns CategorizationResult objects.
  - `refresh_rules`: Updates any rules or data the categorizer uses.
- `GroqTransactionCategorizer`: Implementation using Groq AI to categorize transactions.

### Routes
- `CategoryRouter`: Handles API endpoints for categories.
- `SourceRouter`: Handles API endpoints for sources.
- `TransactionRouter`: Handles API endpoints for transactions.
- `CategorizationRouter`: Handles API endpoints for transaction categorization.
- `TransactionUploader`: Handles uploading and processing transaction data.

### Data Flow
1. Transactions are uploaded through the TransactionUploader.
2. Uncategorized transactions are processed by the TransactionCategorizationService.
3. The service uses a TransactionCategorizer implementation to assign categories.
4. Results are stored in the database through the TransactionsRepository.

## Categorization Process
1. Transactions start with categorization_status = "pending".
2. The categorization service retrieves pending transactions in batches.
3. Each transaction is converted to a CategorizableTransaction object.
4. The categorizer processes these objects and returns CategorizationResult objects.
5. The service updates the transactions with the assigned categories.
6. Categorization status is updated to "categorized" or "failed".

## New Feature: Existing Transactions Categorizer
The new feature will enhance categorization by:
1. Looking for existing transactions with the same normalized description.
2. If found, using the category from those existing transactions.
3. If not found, falling back to another categorizer implementation.
