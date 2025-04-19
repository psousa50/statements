import { useQuery, useMutation, useQueryClient, UseMutationResult } from '@tanstack/react-query';
import { useApiContext } from '../api/ApiContext';
import type { FileUploadResponse, Transaction, StatementSchemaDefinition, FileAnalysisResponse } from '../types';

export const useTransactions = (params?: {
  start_date?: string;
  end_date?: string;
  category_id?: number;
  source_id?: number;
  search?: string;
  skip?: number;
  limit?: number;
}) => {
  const { transactionsApi } = useApiContext();
  return useQuery({
    queryKey: ['transactions', params],
    queryFn: () => transactionsApi.getAll(params),
  });
};

export const useTransaction = (id: number) => {
  const { transactionsApi } = useApiContext();
  return useQuery({
    queryKey: ['transaction', id],
    queryFn: () => transactionsApi.getById(id),
    enabled: !!id,
  });
};

export const useCategories = () => {
  const { categoriesApi } = useApiContext();
  return useQuery({
    queryKey: ['categories'],
    queryFn: () => categoriesApi.getAll(),
  });
};

export const useCategory = (id: number) => {
  const { categoriesApi } = useApiContext();
  return useQuery({
    queryKey: ['category', id],
    queryFn: () => categoriesApi.getById(id),
    enabled: !!id,
  });
};

export const useCreateCategory = () => {
  const queryClient = useQueryClient();
  const { categoriesApi } = useApiContext();
  return useMutation({
    mutationFn: (category: { category_name: string; parent_category_id?: number | null }) =>
      categoriesApi.create(category),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
    },
  });
};

export const useSources = (params?: { skip?: number; limit?: number }) => {
  const { sourcesApi } = useApiContext();
  return useQuery({
    queryKey: ['sources', params],
    queryFn: () => sourcesApi.getAll(params),
  });
};

export const useCreateSource = () => {
  const queryClient = useQueryClient();
  const { sourcesApi } = useApiContext();
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
  const { sourcesApi } = useApiContext();
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
  const { sourcesApi } = useApiContext();
  return useMutation({
    mutationFn: (id: number) => sourcesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] });
    },
  });
};

export const useUpdateTransactionCategory = () => {
  const queryClient = useQueryClient();
  const { transactionsApi } = useApiContext();
  return useMutation({
    mutationFn: ({ transactionId, categoryId }: { transactionId: number; categoryId: number }) =>
      transactionsApi.updateCategory(transactionId, categoryId),
    onSuccess: (updatedTransaction) => {
      queryClient.invalidateQueries({ queryKey: ['transaction', updatedTransaction.id] });

      queryClient.setQueryData(['transactions'], (oldData: any) => {
        if (!oldData) return undefined;

        return oldData.map((transaction: Transaction) =>
          transaction.id === updatedTransaction.id ? updatedTransaction : transaction
        );
      });
    },
  });
};

type AnalyzeFileParams = {
  fileContent: string;
  fileName: string;
};

export type StatementAnalysisMutation = UseMutationResult<FileAnalysisResponse, Error, AnalyzeFileParams>;

export const useStatementAnalysis = () => {
  const { uploadApi } = useApiContext();
  return useMutation<FileAnalysisResponse, Error, AnalyzeFileParams>({
    mutationFn: ({ fileContent, fileName }) => uploadApi.analyzeFile(fileContent, fileName),
  });
};

export interface UploadFileParams {
  statement_id: string;
  statement_schema: StatementSchemaDefinition;
}

export type UploadFileMutation = UseMutationResult<FileUploadResponse, Error, UploadFileParams>;

export const useStatementUpload = () => {
  const queryClient = useQueryClient();
  const { uploadApi } = useApiContext();
  return useMutation<FileUploadResponse, Error, UploadFileParams>({
    mutationFn: ({ statement_schema, statement_id }) => uploadApi.uploadFile(statement_schema, statement_id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
    },
  });
}; 