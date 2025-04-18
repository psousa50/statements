import { test, expect, request } from '@playwright/test';
import { ApiClient, SourcesApi, TransactionsApi } from './apiClient';

const FRONTEND_URL = process.env.PLAYWRIGHT_FRONTEND_URL || 'http://localhost:3000';
const BACKEND_URL = process.env.PLAYWRIGHT_BACKEND_URL || 'http://localhost:8000';

let sourceForTestName: string;
let sourceForTestId: { id: number; name: string };

test.describe('Upload Page', () => {
  test.beforeAll(async ({ request }) => {
    const apiClient = new ApiClient(request, BACKEND_URL);
    const sourcesApi = new SourcesApi(apiClient);
    sourceForTestName = `Test Source ${Math.random().toString(36).slice(2, 10)}`
    sourceForTestId = await sourcesApi.ensureExists(sourceForTestName);
  });

  test.beforeEach(async ({ request }) => {
    const apiClient = new ApiClient(request, BACKEND_URL);
    const transactionsApi = new TransactionsApi(apiClient);
    const txs = await transactionsApi.list({ source_id: sourceForTestId.id, skip: 0, limit: 100 });
    for (const tx of txs) {
      await transactionsApi.delete(tx.id);
    }
  });

  test('can upload, reassign, and submit with correct payload', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/upload`);
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.getByRole('button', { name: /Browse Files/i }).click();
    const fileChooser = await fileChooserPromise;

    const randomColName = `RandomCol_${Math.random().toString(36).slice(2, 10)}`;
    const csvContent = [
      `Date,Description,Another Description,Amount,Balance,${randomColName}`,
      `20-Aug-2020,desc 1,another desc 1,10,100,someval1`,
      `21-Aug-2020,desc 2,another desc 2,20,200,someval2`,
      `22-Aug-2020,desc 2,another desc 3,30,300,someval3`,
    ].join('\n');
    const filePayload = {
      name: 'ForUpload.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent, 'utf-8')
    };
    await fileChooser.setFiles(filePayload);

    await page.getByLabel(/source/i).selectOption({ label: sourceForTestName });

    const columnSelects = page.locator('table select');

    await columnSelects.nth(1).selectOption({ value: 'ignore' });
    await columnSelects.nth(2).selectOption({ value: 'description' });

    await page.getByLabel(/header row/i).fill('1');
    await page.getByLabel(/data starts at row/i).fill('3');

    await page.route('**/transactions/upload', async (route, request) => {
      const postData = JSON.parse(request.postData() ?? '{}');
      expect(postData).toMatchObject({
        statement_id: expect.any(String),
        statement_schema: {
          id: expect.any(String),
          source_id: sourceForTestId.id,
          file_type: 'CSV',
          column_mapping: {
            amount: 'Amount',
            balance: 'Balance',
            date: 'Date',
            description: 'Description',
          },
          header_row: 1,
          start_row: 3,
        },
      });
      await route.continue();
    });

    await page.getByRole('button', { name: /finalize upload/i }).click();

    await expect(page.getByRole('alert')).toHaveClass(/alert-success/);

    const apiRequestContext = await request.newContext({ baseURL: BACKEND_URL });
    const apiClient = new ApiClient(apiRequestContext, BACKEND_URL);
    const transactionsApi = new TransactionsApi(apiClient);
    const transactions = await transactionsApi.list({ source_id: sourceForTestId.id, skip: 0, limit: 10 });
    expect(transactions.length).toBe(2);
    const sortedTransactions = transactions
      .slice(0, 2)
      .sort((a, b) => a.id - b.id);
    const expected = [
      {
        date: '2020-08-21',
        description: 'another desc 2',
        amount: 20,
        balance: 200
      },
      {
        date: '2020-08-22',
        description: 'another desc 3',
        amount: 30,
        balance: 300
      }
    ];
    for (let i = 0; i < expected.length; i++) {
      const t = sortedTransactions[i];
      const exp = expected[i];
      expect(t.date).toBe(exp.date);
      expect(t.normalized_description || t.description).toBe(exp.description);
      expect(Number(t.amount)).toBe(Number(exp.amount));
      expect(Number(t.balance)).toBe(Number(exp.balance));
    }
  });
});
