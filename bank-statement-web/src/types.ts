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

export interface StatementSchemaDefinition {
  id: string;
  source_id?: number;
  file_type: string;
  column_mapping: ColumnMapping;
  start_row: number;
  header_row: number;
}

export interface FileAnalysisResponse {
  statement_id: string;
  statement_schema: StatementSchemaDefinition;
  total_transactions: number;
  total_amount: number;
  date_range_start: string;
  date_range_end: string;
  preview_rows: any[][];
}

export interface UploadResult {
  success: boolean;
  message: string;
  processed: number;
  skipped: number;
}
