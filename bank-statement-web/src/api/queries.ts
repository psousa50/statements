import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transactionsApi, categoriesApi } from './api';
import { Transaction, Category } from '../types';

// Transactions queries
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

// Categories queries
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

// Mutations
export const useUpdateTransactionCategory = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ transactionId, categoryId }: { transactionId: number; categoryId: number }) => 
      transactionsApi.updateCategory(transactionId, categoryId),
    onSuccess: (updatedTransaction) => {
      // Invalidate the specific transaction query
      queryClient.invalidateQueries({ queryKey: ['transaction', updatedTransaction.id] });
      
      // Update the transaction in the transactions list cache
      queryClient.setQueryData<Transaction[]>(['transactions'], (oldData) => {
        if (!oldData) return undefined;
        
        return oldData.map(transaction => 
          transaction.id === updatedTransaction.id ? updatedTransaction : transaction
        );
      });
    },
  });
};
