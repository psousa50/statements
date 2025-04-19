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
  transactionsProcessed: number;
  skippedDuplicates: number;
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
  sourceId?: number;
  fileType: string;
  columnMapping: ColumnMapping;
  startRow: number;
  headerRow: number;
}

export interface FileAnalysisResponse {
  statementId: string;
  statementSchema: StatementSchemaDefinition;
  totalTransactions: number;
  totalAmount: number;
  dateRangeStart: string;
  dateRangeEnd: string;
  previewRows: any[][];
}

export interface UploadResult {
  success: boolean;
  message: string;
  transactionsProcessed: number;
  skippedDuplicates: number;
}
