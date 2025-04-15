import axios from 'axios';
import { Transaction, Category, Source, FileUploadResponse, StatementSchema, FileAnalysisResponse } from '../types';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const transactionsApi = {
  getAll: async (params?: {
    start_date?: string;
    end_date?: string;
    category_id?: number;
    source_id?: number;
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<Transaction[]> => {
    const response = await api.get('/transactions', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Transaction> => {
    const response = await api.get(`/transactions/${id}`);
    return response.data;
  },

  updateCategory: async (transactionId: number, categoryId: number): Promise<Transaction> => {
    const response = await api.patch(`/transactions/${transactionId}`, {
      category_id: categoryId
    });
    return response.data;
  },
};

export const categoriesApi = {
  getAll: async (): Promise<Category[]> => {
    const response = await api.get('/categories');
    return response.data;
  },

  getById: async (id: number): Promise<Category> => {
    const response = await api.get(`/categories/${id}`);
    return response.data;
  },

  create: async (category: { category_name: string; parent_category_id?: number | null }): Promise<Category> => {
    const response = await api.post('/categories', category);
    return response.data;
  },
};

export const sourcesApi = {
  getAll: async (params?: { skip?: number; limit?: number }): Promise<Source[]> => {
    const response = await api.get('/sources', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Source> => {
    const response = await api.get(`/sources/${id}`);
    return response.data;
  },

  create: async (source: { name: string; description?: string }): Promise<Source> => {
    const response = await api.post('/sources', source);
    return response.data;
  },

  update: async (id: number, source: { name: string; description?: string }): Promise<Source> => {
    const response = await api.put(`/sources/${id}`, source);
    return response.data;
  },

  delete: async (id: number): Promise<Source> => {
    const response = await api.delete(`/sources/${id}`);
    return response.data;
  },
};

export const uploadApi = {
  uploadFile: async (
    statementSchema?: StatementSchema,
    statement_id?: string
  ): Promise<FileUploadResponse> => {
    // Create the request body with just the statement schema
    const body = {
      statement_id: statement_id,
      statement_schema: statementSchema
    };

    const response = await api.post('/transactions/upload', body, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    return response.data;
  },

  analyzeFile: async (fileContent: string, fileName: string): Promise<FileAnalysisResponse> => {
    const body = {
      file_content: fileContent,
      file_name: fileName
    };

    const response = await api.post('/transactions/analyze', body, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    return response.data;
  }
};

export default api;
