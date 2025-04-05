export interface Transaction {
  id: number;
  date: string;
  description: string;
  normalized_description: string;
  amount: number;
  currency: string;
  category_id: number | null;
  source_id: number;
  category?: Category;
  source?: Source;
}

export interface Category {
  id: number;
  category_name: string;
  description: string | null;
}

export interface Source {
  id: number;
  name: string;
  description: string | null;
}

export interface FileUploadResponse {
  message: string;
  transactions_processed: number;
  transactions: Transaction[];
  skipped_duplicates: number;
}
