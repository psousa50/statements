import React, { createContext, useContext } from 'react';
import { transactionsApi, categoriesApi, sourcesApi, uploadApi } from './api';

export interface ApiContextType {
  transactionsApi: typeof transactionsApi;
  categoriesApi: typeof categoriesApi;
  sourcesApi: typeof sourcesApi;
  uploadApi: typeof uploadApi;
}

export const ApiContext = createContext<ApiContextType | undefined>(undefined);

export const ApiProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ApiContext.Provider value={{
    transactionsApi,
    categoriesApi,
    sourcesApi,
    uploadApi,
  }}>
    {children}
  </ApiContext.Provider>
);

export function useApiContext(): ApiContextType {
  const ctx = useContext(ApiContext);
  if (!ctx) throw new Error('useApiContext must be used within an ApiProvider');
  return ctx;
}
