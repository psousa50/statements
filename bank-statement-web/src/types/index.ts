export interface Transaction {
  id: number;
  date: string;
  description: string;
  normalizedDescription: string;
  amount: number;
  currency: string;
  categoryId: number | null;
  sourceId: number;
  category?: Category;
  source?: Source;
}

export interface Category {
  id: number;
  category_name: string;
  parent_category_id: number | null;
}

export interface Source {
  id: number;
  name: string;
  description: string | null;
}

export interface FileUploadResponse {
  message: string;
  transactionsProcessed: number;
  transactions: Transaction[];
  skippedDuplicates: number;
}
