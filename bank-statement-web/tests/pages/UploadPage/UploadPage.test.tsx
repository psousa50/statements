import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ApiContext, ApiContextType } from '../../../src/api/ApiContext';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import UploadPage from '../../../src/pages/UploadPage/UploadPage';

const analysisResult = {
  num_transactions: 2354,
  total_amount: 223,
  currency: 'Eur',
  start_date: '2023-03-02',
  end_date: '2024-04-23',
  statement_schema: {
    column_mapping: {
      date: 'Date',
      description: 'Description',
      amount: 'Amount',
    },
    header_row: 0,
    start_row: 1,
    source_id: 1,
  },
  preview_rows: [
    ['Date', 'Description', 'Amount'],
    ['2024-01-01', 'Test', '100'],
  ],
};
const sources = [
  { id: 1, name: 'Revolut' },
  { id: 2, name: 'Source 1' },
  { id: 3, name: 'Source 2' },
  { id: 4, name: 'Source 3' },
];

const mockApis: ApiContextType = {
  transactionsApi: {
    getAll: jest.fn(),
    getById: jest.fn(),
    updateCategory: jest.fn(),
  },
  categoriesApi: {
    getAll: jest.fn(),
    getById: jest.fn(),
    create: jest.fn(),
  },
  sourcesApi: {
    getAll: jest.fn().mockResolvedValue(sources),
    getById: jest.fn(),
    create: jest.fn(),
    update: jest.fn(),
    delete: jest.fn(),
  },
  uploadApi: {
    uploadFile: jest.fn(),
    analyzeFile: jest.fn().mockResolvedValue(analysisResult),
  },
};

const queryClient = new QueryClient();

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <ApiContext.Provider value={mockApis}>
        {ui}
      </ApiContext.Provider>
    </QueryClientProvider>
  );
};

async function simulateUpload() {
  const file = new File(['dummy content'], 'statement.csv', { type: 'text/csv' });
  const input = document.querySelector('input[type="file"]') as HTMLInputElement;
  fireEvent.change(input, { target: { files: [file] } });
  await screen.findByTestId('analysis-summary-panel');
}

describe('UploadPage analysis summary and source selector', () => {
  it('shows compact analysis summary after analysis', async () => {
    renderWithProviders(
      <UploadPage />
    );
    await simulateUpload();
    expect(screen.getByRole('button', { name: /Revolut/ })).toHaveTextContent(/Revolut/);
    expect(screen.getByText(/Number of Transactions/i)).toBeInTheDocument();
    expect(screen.getByText(/2,354/)).toBeInTheDocument();
    expect(screen.getByText(/Total amount/i)).toBeInTheDocument();
    expect(screen.getByText(/Eur 223/)).toBeInTheDocument();
    expect(screen.getByText(/From 2023-03-02 to 2024-04-23/)).toBeInTheDocument();
  });

  it('shows source popup and updates source on selection', async () => {
    renderWithProviders(
      <UploadPage />
    );
    await simulateUpload();
    fireEvent.click(screen.getByRole('button', { name: /Revolut/ }));
    expect(screen.getByRole('menu')).toBeVisible();
    expect(screen.getByRole('menuitem', { name: /Source 1/i })).toBeVisible();
    expect(screen.getByRole('menuitem', { name: /Source 2/i })).toBeVisible();
    expect(screen.getByRole('menuitem', { name: /Source 3/i })).toBeVisible();
    fireEvent.click(screen.getByRole('menuitem', { name: /Source 2/i }));
    expect(screen.getByRole('button', { name: /Source 2/ })).toHaveTextContent(/Source 2/);
  });
});

describe('UploadPage layout and source selector', () => {
  it('renders analysis summary and source selector as full-width panels above the table', async () => {
    renderWithProviders(<UploadPage />);
    await simulateUpload();
    const summary = screen.getByTestId('analysis-summary-panel');
    const selector = screen.getByTestId('source-selector-panel');
    expect(summary).toBeVisible();
    expect(selector).toBeVisible();
    expect(summary).toHaveStyle({ width: '100%' });
    expect(selector).toHaveStyle({ width: '100%' });
  });

  it('shows a menu to the right of the source button, highlights options on hover, and updates selection', async () => {
    renderWithProviders(<UploadPage />);
    await simulateUpload();
    const button = await screen.findByRole('button', { name: /^Source:/i });
    fireEvent.click(button);
    const menu = screen.getByRole('menu');
    expect(menu).toBeVisible();
    const option2 = screen.getByRole('menuitem', { name: /Source 2/i });
    fireEvent.mouseOver(option2);
    expect(option2).toHaveClass('highlighted');
    fireEvent.click(option2);
    expect(button).toHaveTextContent(/Source 2/);
  });
});
