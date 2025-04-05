# Project Setup
	1.	Initialize Project Structure
	•	Create a new directory (e.g., bank-statement-api).
	•	Set up a Python virtual environment.
	•	Install required dependencies:
	•	fastapi for the web framework
	•	uvicorn as the development server
	•	psycopg2 or asyncpg for database interaction (depending on sync vs. async)
	•	Libraries for file parsing (e.g., pandas if we need advanced CSV/Excel handling)
	2.	Database Configuration
	•	Use PostgreSQL as the primary database.
	•	Create a database schema to store transactions and categories.
	•	Example environment variables:
	•	DATABASE_URL (e.g., postgresql://user:password@localhost:5432/bankstatements)

⸻

## Data Model

The database will focus on two tables (plus optional supporting tables if needed):
	1.	Transactions
	•	id (Primary Key)
	•	date (Date or Timestamp)
	•	description (Text)
	•	amount (Numeric)
	•	category_id (Foreign Key to Categories)
	•	Optional columns for metadata: e.g., currency, account_id, etc.
	2.	Categories
	•	id (Primary Key)
	•	category_name (Text)
	•	Optional parent_category_id or other hierarchical fields if subcategories are needed.

⸻

## File Processing and Categorization Logic
	1.	File Format Detection
	•	Read the uploaded file and use simple heuristics or a library (like pandas) to check if it’s CSV, Excel, or another format.
	2.	Data Extraction
	•	Once the format is identified, parse the file’s rows into a Python data structure.
	•	Map columns to known fields: date, description, amount.
	•	Possibly handle currency or other columns if needed.
	3.	Basic Categorization Algorithm
	•	Define a simple rule-based or keyword-based approach:
	•	If description contains “Grocery” or “Supermarket,” category is “Groceries.”
	•	If description contains “Uber,” category is “Transport.”
	•	Alternatively, store transactions first as Uncategorized, then run a classification step that updates the category.
	•	The goal is to keep it simple for the MVP.
	4.	Data Insertion
	•	After categorizing or labeling transactions, insert them into the Transactions table, linking each to a category in Categories.

⸻

## Endpoints

Use FastAPI to create a simple REST API with these core endpoints:
	1.	POST /upload
	•	Accepts multipart file upload.
	•	Reads and parses the file (CSV/Excel).
	•	Applies simple categorization.
	•	Inserts transactions (and any new categories if needed) into the database.
	•	Returns a success message or the inserted records.
	2.	GET /transactions
	•	Returns a list of transactions, possibly supporting basic filters:
	•	e.g., date range, category, or search by description.
	•	The response should include relevant fields (id, date, description, amount, category_name).
	3.	GET /categories
	•	Returns a list of available categories.
	•	Could also return subcategories if that structure is implemented.

(Optional) POST /categorize
	•	Accepts transaction descriptions, returns a guessed category.
	•	Could be part of a more advanced workflow if needed.

⸻

## 5. High-Level Flow
	1.	Client Upload
	•	The client (web or mobile app) sends a file via the POST /upload endpoint.
	2.	Backend Processing
	•	The backend detects the file type, parses it, and maps the data to the transaction model.
	•	A simple categorization step is applied (e.g., rule-based).
	3.	Database Insertion
	•	Transactions are stored in the Transactions table, with category links.
	•	If new categories are found or created dynamically, they are stored in the Categories table.
	4.	Retrieving Data
	•	The client requests transactions using GET /transactions.
	•	The client retrieves categories using GET /categories.

⸻
 
## 6. Implementation Details
	1.	Async vs. Sync
	•	Decide whether to use FastAPI in asynchronous mode with an async PG driver or synchronous mode with blocking DB calls.
	•	For a small MVP, a sync approach using psycopg2 is sufficient; can optimize later.
	2.	Schema Setup and Migrations
	•	Use either raw SQL or a migration tool (e.g., Alembic) to create initial tables.
	•	Script out creation of the transactions and categories tables.
	3.	File Size and Validation
	•	Consider potential size limits and parse time.
	•	Validate the correctness of the data (e.g., check columns).
	•	If needed, store the file in a temporary location before parsing.
	4.	Error Handling
	•	Return meaningful errors if the file is invalid or parsing fails.
	•	Use FastAPI’s exception handling to send appropriate HTTP status codes.
	5.	Performance Considerations
	•	For an MVP, focus on correctness over heavy optimization.
	•	Ensure indexes on frequently queried fields (e.g., category_id, date).

## 7. A possible project structure

statements-monorepo/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes/
│   │   │   ├── transactions.py
│   │   │   └── categories.py
│   │   ├── services/
│   │   │   └── categorizer.py
│   │   └── db.py
│   ├── migrations/
│   ├── requirements.txt
│   └── README.md
├── web/
│   ├── ... (e.g., React/Vue/Angular code)
│   ├── package.json (if JavaScript-based)
│   └── README.md
├── mobile/
│   ├── ... (e.g., React Native/Flutter code)
│   ├── package.json / pubspec.yaml (depending on framework)
│   └── README.md
└── README.md

For now we are only working on the backend, do not create the web and mobile directories.

## 7. Next Steps
	•	Testing: Write unit tests (e.g., Pytest) for file parsing, categorization logic, and endpoints.
	•	Deployment: Deploy on a preferred cloud platform (e.g., Heroku, AWS).
	•	Extensions: Add better categorization (machine learning), user management, advanced reporting, etc., once MVP is validated.