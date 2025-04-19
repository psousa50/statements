import React from 'react';
import { useCategories, useUpdateTransactionCategory } from '../hooks/useQueries';
import { Transaction, Category } from '../types';

interface TransactionCategoryEditorProps {
  transaction: Transaction;
}

export const TransactionCategoryEditor: React.FC<TransactionCategoryEditorProps> = ({
  transaction
}) => {
  const { data: categories, isLoading: categoriesLoading } = useCategories();
  const updateCategory = useUpdateTransactionCategory();

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newCategoryId = parseInt(e.target.value, 10);

    updateCategory.mutate(
      {
        transactionId: transaction.id,
        categoryId: newCategoryId
      },
      {
        onError: (error) => {
          console.error('Failed to update category:', error);
        }
      }
    );
  };

  if (categoriesLoading) return <span>Loading categories...</span>;

  return (
    <select
      value={transaction.categoryId || ''}
      onChange={handleCategoryChange}
      disabled={updateCategory.isPending}
      className={updateCategory.isPending ? 'opacity-50' : ''}
    >
      <option value="">Select a category</option>
      {categories?.map((category: Category) => (
        <option key={category.id} value={category.id}>
          {category.categoryName}
        </option>
      ))}
    </select>
  );
}
