import axios from 'axios';
import {
  Transaction,
  Category,
  Source,
  StatementUploadResponse,
  StatementAnalysisResponse,
} from '../types';
import { UploadStatementRequest } from '../hooks/useQueries';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

function toSnakeCase(obj?: any) {
  return Object.fromEntries(
    Object.entries(obj || {}).map(([key, value]) => [
      key.replace(/([A-Z])/g, '_$1').toLowerCase(),
      value,
    ])
  );
}

export const transactionsApi = {
  getAll: async (params?: {
    startDate?: string;
    endDate?: string;
    categoryId?: number;
    sourceId?: number;
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<Transaction[]> => {
    const response = await api.get('/transactions', {
      params: toSnakeCase(params),
    });
    return response.data;
  },

  getById: async (id: number): Promise<Transaction> => {
    const response = await api.get(`/transactions/${id}`);
    return response.data;
  },

  updateCategory: async (
    transactionId: number,
    categoryId: number
  ): Promise<Transaction> => {
    const response = await api.patch(`/transactions/${transactionId}`, {
      categoryId: categoryId,
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

  create: async (category: {
    categoryName: string;
    parentCategoryId?: number | null;
  }): Promise<Category> => {
    const response = await api.post('/categories', category);
    return response.data;
  },
};

export const sourcesApi = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
  }): Promise<Source[]> => {
    const response = await api.get('/sources', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Source> => {
    const response = await api.get(`/sources/${id}`);
    return response.data;
  },

  create: async (source: {
    name: string;
    description?: string;
  }): Promise<Source> => {
    const response = await api.post('/sources', source);
    return response.data;
  },

  update: async (
    id: number,
    source: { name: string; description?: string }
  ): Promise<Source> => {
    const response = await api.put(`/sources/${id}`, source);
    return response.data;
  },

  delete: async (id: number): Promise<Source> => {
    const response = await api.delete(`/sources/${id}`);
    return response.data;
  },
};

export const uploadApi = {
  uploadStatement: async (
    uploadStatementParams: UploadStatementRequest
  ): Promise<StatementUploadResponse> => {
    const response = await api.post(
      '/transactions/upload',
      uploadStatementParams,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    return response.data;
  },

  analyzeFile: async (
    formData: FormData
  ): Promise<StatementAnalysisResponse> => {
    const response = await api.post('/transactions/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },
};

export default api;
