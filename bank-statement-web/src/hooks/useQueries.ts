import {
  useQuery,
  useMutation,
  useQueryClient,
  UseMutationResult,
} from '@tanstack/react-query';
import { useApiContext } from '../api/ApiContext';
import type {
  StatementUploadResponse,
  Transaction,
  StatementSchemaDefinition,
  StatementAnalysisResponse as StatementAnalysisResponse,
} from '../types';

export const useTransactions = (params?: {
  startDate?: string;
  endDate?: string;
  categoryId?: number;
  sourceId?: number;
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
    mutationFn: (category: {
      categoryName: string;
      parentCategoryId?: number | null;
    }) => categoriesApi.create(category),
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
    mutationFn: ({
      id,
      source,
    }: {
      id: number;
      source: { name: string; description?: string };
    }) => sourcesApi.update(id, source),
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
    mutationFn: ({
      transactionId,
      categoryId,
    }: {
      transactionId: number;
      categoryId: number;
    }) => transactionsApi.updateCategory(transactionId, categoryId),
    onSuccess: (updatedTransaction) => {
      queryClient.invalidateQueries({
        queryKey: ['transaction', updatedTransaction.id],
      });

      queryClient.setQueryData(['transactions'], (oldData: any) => {
        if (!oldData) return undefined;

        return oldData.map((transaction: Transaction) =>
          transaction.id === updatedTransaction.id
            ? updatedTransaction
            : transaction
        );
      });
    },
  });
};

export type StatementAnalysisMutation = UseMutationResult<
  StatementAnalysisResponse,
  Error,
  FormData
>;

export const useStatementAnalysis = () => {
  const { uploadApi } = useApiContext();
  return useMutation<StatementAnalysisResponse, Error, FormData>({
    mutationFn: (formData) => uploadApi.analyzeFile(formData),
  });
};

export interface UploadStatementRequest {
  statementId: string;
  statementSchema: StatementSchemaDefinition;
}

export type UploadStatementMutation = UseMutationResult<
  StatementUploadResponse,
  Error,
  UploadStatementRequest
>;

export const useStatementUpload = () => {
  const queryClient = useQueryClient();
  const { uploadApi } = useApiContext();
  return useMutation<StatementUploadResponse, Error, UploadStatementRequest>({
    mutationFn: (uploadStatementParams) =>
      uploadApi.uploadStatement(uploadStatementParams),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
    },
  });
};
