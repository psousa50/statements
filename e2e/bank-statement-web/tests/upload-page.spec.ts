import { test, expect } from '@playwright/test';

test.describe('Upload Page', () => {
  test('can upload, reassign, and submit with correct payload', async ({ page }) => {
    await page.goto('http://localhost:3000/upload');
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
          source_id: 2,
          file_type: 'CSV',
          column_mapping: {
            amount: 'Amount2',
            balance: 'Balance2',
            date: 'Date2',
            description: 'Another Description2',
          },
          column_names: [
            'Date',
            'Description',
            'Another Description',
            'Amount',
            'Balance',
          ],
          header_row: 1,
          start_row: 3,
        },
      });
      await route.continue();
    });

    await page.getByRole('button', { name: /finalize upload/i }).click();
  });
});
