import { test, expect, request } from '@playwright/test';
import { ApiClient, SourcesApi } from './apiClient';

const FRONTEND_URL = process.env.PLAYWRIGHT_FRONTEND_URL || 'http://localhost:3000';
const BACKEND_URL = process.env.PLAYWRIGHT_BACKEND_URL || 'http://localhost:8000';

let ab7Source: { id: number; name: string };

test.describe('Upload Page', () => {
  test.beforeAll(async ({ request }) => {
    const apiClient = new ApiClient(request, BACKEND_URL);
    const sourcesApi = new SourcesApi(apiClient);
    ab7Source = await sourcesApi.ensureExists('AB7');
  });

  test('can upload, reassign, and submit with correct payload', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/upload`);
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.getByRole('button', { name: /Browse Files/i }).click();
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles('fixtures/ForUpload.csv');

    await page.getByLabel(/source/i).selectOption({ label: 'AB7' });

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
          source_id: ab7Source.id,
          file_type: 'CSV',
          column_mapping: {
            amount: 'Amount2',
            balance: 'Balance2',
            date: 'Date2',
            description: 'Another Description2',
          },
          header_row: 1,
          start_row: 3,
        },
      });
      await route.continue();
    });

    await page.getByRole('button', { name: /finalize upload/i }).click();

    await expect(page.getByRole('alert')).toHaveClass(/alert-success/);
  });
});
