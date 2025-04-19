export interface Transaction {
  id: number;
  date: string;
  description: string;
  normalizedDescription: string;
  amount: number;
  categoryId: number | null;
  sourceId: number;
  categorizationStatus?: string;
}

export interface Category {
  id: number;
  categoryName: string;
  parentCategoryId: number | null;
}

export interface Source {
  id: number;
  name: string;
  description?: string;
}

export interface StatementUploadResponse {
  message: string;
  transactionsProcessed: number;
  skippedDuplicates: number;
}

export interface ColumnMapping {
  date: string;
  description: string;
  amount: string;
  debitAmount?: string;
  creditAmount?: string;
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

export interface StatementAnalysisResponse {
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
