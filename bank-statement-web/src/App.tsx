import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ApiProvider } from './api/ApiContext';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import UserHomePage from './pages/UserHomePage';
import UploadPage from './pages/UploadPage';
import TransactionsPage from './pages/TransactionsPage';
import CategoriesPage from './pages/CategoriesPage';
import SourcesPage from './pages/SourcesPage';
import ChartsPage from './pages/ChartsPage';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ApiProvider>
        <BrowserRouter>
          <div className="App">
            <Navigation />
            <div className="content-container pt-5 mt-4">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/user-home" element={<UserHomePage />} />
                <Route path="/upload" element={<UploadPage />} />
                <Route path="/transactions" element={<TransactionsPage />} />
                <Route path="/charts" element={<ChartsPage />} />
                <Route path="/categories" element={<CategoriesPage />} />
                <Route path="/sources" element={<SourcesPage />} />
              </Routes>
            </div>
          </div>
        </BrowserRouter>
      </ApiProvider>
    </QueryClientProvider>
  );
}

export default App;
