export interface Transaction {
  id: number;
  date: string;
  description: string;
  normalized_description: string;
  amount: number;
  category_id: number | null;
  source_id: number;
  categorization_status?: string;
}

export interface Category {
  id: number;
  category_name: string;
  parent_category_id: number | null;
}

export interface Source {
  id: number;
  name: string;
  description?: string;
}

export interface FileUploadResponse {
  message: string;
  transactions_processed: number;
  transactions: Transaction[];
  skipped_duplicates: number;
}

export interface ColumnMapping {
  date: string;
  description: string;
  amount: string;
  debit_amount?: string;
  credit_amount?: string;
  currency?: string;
  balance?: string;
}

export interface StatementSchema {
  id: string;
  source_id: number | null;
  file_type: string;
  column_mapping: ColumnMapping;
  start_row: number;
  header_row: number;
  column_names: string[];
}

export interface FileAnalysisResponse {
  statement_schema: StatementSchema;
  total_transactions: number;
  total_amount: number;
  date_range_start: string | null;
  date_range_end: string | null;
  file_id: string;
  preview_rows: any[][];
}
