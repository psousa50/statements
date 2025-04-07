import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transactionsApi, categoriesApi, sourcesApi, uploadApi } from '../api/api';
import type { FileUploadResponse } from '../types';

// Transaction queries
export const useTransactions = (params?: {
  start_date?: string;
  end_date?: string;
  category_id?: number;
  source_id?: number;
  search?: string;
  skip?: number;
  limit?: number;
}) => {
  return useQuery({
    queryKey: ['transactions', params],
    queryFn: () => transactionsApi.getAll(params),
  });
};

export const useTransaction = (id: number) => {
  return useQuery({
    queryKey: ['transaction', id],
    queryFn: () => transactionsApi.getById(id),
    enabled: !!id,
  });
};

// Category queries
export const useCategories = () => {
  return useQuery({
    queryKey: ['categories'],
    queryFn: () => categoriesApi.getAll(),
  });
};

export const useCategory = (id: number) => {
  return useQuery({
    queryKey: ['category', id],
    queryFn: () => categoriesApi.getById(id),
    enabled: !!id,
  });
};

export const useCreateCategory = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (category: { category_name: string; parent_category_id?: number | null }) => 
      categoriesApi.create(category),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
    },
  });
};

// Source queries
export const useSources = (params?: { skip?: number; limit?: number }) => {
  return useQuery({
    queryKey: ['sources', params],
    queryFn: () => sourcesApi.getAll(params),
  });
};

export const useSource = (id: number) => {
  return useQuery({
    queryKey: ['source', id],
    queryFn: () => sourcesApi.getById(id),
    enabled: !!id,
  });
};

export const useCreateSource = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (source: { name: string; description?: string }) => 
      sourcesApi.create(source),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] });
    },
  });
};

export const useUpdateSource = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, source }: { id: number; source: { name: string; description?: string } }) => 
      sourcesApi.update(id, source),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] });
    },
  });
};

export const useDeleteSource = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => sourcesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] });
    },
  });
};

// File upload mutation
export const useFileUpload = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ file, sourceId }: { file: File; sourceId?: number }): Promise<FileUploadResponse> => 
      uploadApi.uploadFile(file, sourceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
    },
  });
};
