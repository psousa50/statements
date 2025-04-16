import { test, expect } from '@playwright/test';

test.describe('Upload Page', () => {
  test('shows the upload button', async ({ page }) => {
    await page.goto('http://localhost:3000/upload');
    const uploadButton = await page.getByRole('button', { name: /Browse Files/i });
    await expect(uploadButton).toBeVisible();
  });

  test('processes file and shows analysis summary with transactions', async ({ page }) => {
    await page.goto('http://localhost:3000/upload');
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.getByRole('button', { name: /Browse Files/i }).click();
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles('fixtures/100 BT Records.csv');
    // Wait for the analysis summary card to appear
    const analysisSummary = page.getByRole('heading', { name: /analysis summary/i }).locator('..').locator('..');
    const transactionsPanel = analysisSummary.getByText(/transactions/i, { exact: false });
    await expect(transactionsPanel).toBeVisible();
    await expect(analysisSummary.getByText('100', { exact: true })).toBeVisible();
  });
});
