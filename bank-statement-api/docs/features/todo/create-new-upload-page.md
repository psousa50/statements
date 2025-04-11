# Objective

Create a clear, functional, and visually beautiful UI for users to upload bank statements, review extracted data, adjust settings, and finalize the upload.

## Features & Flow

1. Upload Section

- Drag-and-drop file area

- Button to browse local files

- Shows file type and size limit (e.g., CSV, XLSX, max 10MB)

- After selection: show a loading spinner and send the file to the backend for analysis

2. Analysis Summary (Returned from Backend)

- Detected source (e.g., bank name or format)

- Number of rows

- Total amount (sum of "Amount" column)

- Date range (if available)

- First few rows of data as preview (up to 10)

3. Editable Column Mapping Table

- Table with header row and 10 preview rows

- Each column has a dropdown above it to set column type:

  - Description

Amount

Date

Category (optional)

Ignore

Show which row is treated as the header

Allow user to set start of data row if parsing was incorrect

4. Validation & Warnings

Ensure required columns (Amount, Date) are mapped

Highlight if values seem off (e.g., blank cells, unusual values)

Help icons or tooltips to explain each column type

5. Final Actions

"Finalize Upload" button (disabled until valid mappings)

Optional: "Cancel" or "Start Over"

Optional: "Save Mapping as Template"

Optional: "Preview Categorization"


🛠️ Component Structure
<UploadPage>
└─ <FileUploadZone />
    ├─ Handles drag & drop or file selection
    └─ Shows spinner during parsing

<AnalysisSummary />
    ├─ Source, rows, date range, total amount
    └─ Basic info cards (modular)

<ColumnMappingTable />
    ├─ Table with editable header types
    └─ Controls for start row selection
    └─ Show preview first rows

<ValidationMessages />
    └─ Error or warning banners for missing fields

<UploadFooter />
    ├─ Finalize Upload button
    ├─ Cancel / Start Over
    └─ Optional features (template, preview)

Response sample from first upload:
```json
{
  "source": "Revolut",
  "total_transactions": 10,
  "total_amount": 100.00,
  "date_range_start": "2023-01-01", 
  "date_range_end": "2023-01-31",
  "column_mappings": {
    "date": "Date",
    "description": "Description",
    "amount": "Value"
  },
  "start_row": 1,
  "file_id": "uuid-from-previous-upload"
}
```

The backend will return this response after the first upload. The frontend will use this response to populate the column mapping table and show the analysis summary.

A new request will be made to the backend with the same schema


