import React from 'react';
import { useCategories, useUpdateTransactionCategory } from '../api/queries';
import { Category } from '../types';

interface CategorySelectorProps {
  transactionId: number;
  currentCategoryId: number | null;
}

export const CategorySelector: React.FC<CategorySelectorProps> = ({ 
  transactionId, 
  currentCategoryId 
}) => {
  const { data: categories, isLoading: categoriesLoading } = useCategories();
  const updateCategory = useUpdateTransactionCategory();
  
  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newCategoryId = parseInt(e.target.value, 10);
    
    updateCategory.mutate(
      { 
        transactionId, 
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
      value={currentCategoryId || ''}
      onChange={handleCategoryChange}
      disabled={updateCategory.isPending}
      className={updateCategory.isPending ? 'opacity-50' : ''}
    >
      <option value="">Select a category</option>
      {categories?.map((category: Category) => (
        <option key={category.id} value={category.id}>
          {category.category_name}
        </option>
      ))}
    </select>
  );
};
