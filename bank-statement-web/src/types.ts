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
