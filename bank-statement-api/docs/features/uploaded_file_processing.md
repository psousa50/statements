# 🏛️ High-Level Architecture

```
[ Client UI / API ]
        |
        v
[ Upload Endpoint ]
        |
        v
+--------------------------+
|      File Processor      |  ← Entry point
+--------------------------+
| - Detect file type       |
| - Select appropriate     |
|   parser                 |
+--------------------------+
        |
        v
+--------------------------+
|    Statement Parser      |  ← Abstract base
+--------------------------+
| - parse(file)            |
| - detect_columns(rows)   |
+--------------------------+
     /     |      \
    v      v       v
+------+ +--------+ +--------+
| CSV  | | Excel  | |  PDF   |  ← Specific parsers
+------+ +--------+ +--------+

Each returns:  
[ List[RawTransaction] ]

        |
        v
+--------------------------+
|  Column Normalizer       | ← Maps raw columns to standard fields
+--------------------------+
| - date, amount, desc     |
| - balance (optional)     |
+--------------------------+
        |
        v
+--------------------------+
| Transaction Cleaner      | ← Cleans up and standardizes data
+--------------------------+
| - normalize date formats |
| - convert amounts        |
| - remove noise rows      |
+--------------------------+
        |
        v
+--------------------------+
| Transaction Categorizer  | ← Rules + AI
+--------------------------+
| - Regex & ML-based       |
| - Merchant DB/cache      |
| - Subcategory support    |
+--------------------------+
        |
        v
+--------------------------+
|  ParsedStatement Object  | ← Ready to store / return
+--------------------------+
| - metadata (source, acc) |
| - transactions[]         |
+--------------------------+
```

🌐 Components Overview

1. File Processor
	•	Handles upload
	•	Extracts content or streams
	•	Uses file type to select the parser

2. Statement Parser Interface
	•	Defines contract: parse(), detect_columns()
	•	Allows easy addition of new formats

3. Column Normalizer
	•	Maps varied column headers (e.g., “Txn Date”, “Date of Transaction”) to canonical names
	•	Uses fuzzy matching or ML

4. Transaction Cleaner
	•	Deals with:
	•	Negative/positive values
	•	Dates in multiple formats
	•	Extra rows (headers, totals)

5. Transaction Categorizer
	•	Assigns categories and subcategories
	•	Uses:
	•	Rule-based classification
	•	Optional ML/LLM for edge cases
	•	User-corrected feedback loop

6. ParsedStatement
	•	Final structured representation
	•	Holds:
	•	Metadata (bank, account type)
	•	List of cleaned, categorized transactions
	•	Optional: summary (totals, by category)

⸻

💡 Backend Flow Summary
	1.	Upload hits /upload-statement
	2.	File is streamed to FileProcessor
	3.	Parser is selected dynamically
	4.	Transactions are extracted (raw)
	5.	Columns are mapped → canonical schema
	6.	Data is cleaned and normalized
	7.	Transactions are categorized
	8.	Result is stored or returned

