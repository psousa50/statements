# Bank Statement API

A FastAPI-based REST API for processing, categorizing, and managing bank statements.

## Features

- Upload bank statements in CSV or Excel format
- Automatic transaction categorization
- Query transactions with filtering options
- Manage transaction categories

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -e .
   ```

3. Configure environment variables:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/bankstatements
   ```

4. Run database migrations:
   ```
   alembic upgrade head
   ```

5. Start the development server:
   ```
   uvicorn src.app.main:app --reload
   ```

## API Endpoints

- `POST /upload`: Upload and process bank statement files
- `GET /transactions`: Retrieve transactions with optional filters
- `GET /categories`: Get all available transaction categories

## Development

Run tests:
```
pytest
```
