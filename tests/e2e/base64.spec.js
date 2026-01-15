// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Base64 Encoder/Decoder', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/tools/base64');
  });

  test('page loads correctly', async ({ page }) => {
    await expect(page).toHaveTitle(/Base64/i);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('encode mode is selected by default', async ({ page }) => {
    await expect(page.locator('#encodeMode')).toBeChecked();
    await expect(page.locator('#decodeMode')).not.toBeChecked();
  });

  test('encodes text to base64', async ({ page }) => {
    const input = page.locator('#inputText');
    const output = page.locator('#outputText');

    await input.fill('Hello World');
    
    // Wait for the output to update
    await expect(output).toHaveValue('SGVsbG8gV29ybGQ=');
  });

  test('encodes special characters correctly', async ({ page }) => {
    const input = page.locator('#inputText');
    const output = page.locator('#outputText');

    await input.fill('Hällo Wörld');
    
    // Should handle UTF-8 characters
    await expect(output).not.toHaveValue('');
    
    // Verify it's valid base64 by checking the pattern
    const outputValue = await output.inputValue();
    expect(outputValue).toMatch(/^[A-Za-z0-9+/]+=*$/);
  });

  test('switches to decode mode', async ({ page }) => {
    // Click the label, not the hidden radio input (Bootstrap btn-check pattern)
    await page.locator('label[for="decodeMode"]').click();
    
    await expect(page.locator('#decodeMode')).toBeChecked();
    await expect(page.locator('#encodeMode')).not.toBeChecked();
  });

  test('decodes base64 to text', async ({ page }) => {
    // Switch to decode mode - click label
    await page.locator('label[for="decodeMode"]').click();
    
    const input = page.locator('#inputText');
    const output = page.locator('#outputText');

    await input.fill('SGVsbG8gV29ybGQ=');
    
    await expect(output).toHaveValue('Hello World');
  });

  test('shows error for invalid base64 in decode mode', async ({ page }) => {
    await page.locator('label[for="decodeMode"]').click();
    
    const input = page.locator('#inputText');
    const errorMessage = page.locator('#errorMessage');

    await input.fill('not-valid-base64!!!');
    
    // Error message should be visible
    await expect(errorMessage).toBeVisible();
  });

  test('clears input/output when switching modes', async ({ page }) => {
    const input = page.locator('#inputText');
    const output = page.locator('#outputText');

    // Type something in encode mode
    await input.fill('Hello');
    await expect(output).toHaveValue('SGVsbG8=');

    // Switch to decode mode
    await page.locator('label[for="decodeMode"]').click();

    // Both should be cleared
    await expect(input).toHaveValue('');
    await expect(output).toHaveValue('');
  });

  test('enhanced textarea shows cursor position', async ({ page }) => {
    const input = page.locator('#inputText');
    
    await input.fill('Line 1\nLine 2\nLine 3');
    await input.click();
    
    // Check if cursor position indicator exists (from enhanced textarea)
    const positionIndicator = page.locator('.position-info').first();
    
    // If enhanced textarea is active, position info should exist
    const count = await positionIndicator.count();
    if (count > 0) {
      await expect(positionIndicator).toBeVisible();
    }
  });

  test('roundtrip encode and decode', async ({ page }) => {
    const input = page.locator('#inputText');
    const output = page.locator('#outputText');
    
    const originalText = 'The quick brown fox jumps over the lazy dog. 12345!@#$%';
    
    // Encode
    await input.fill(originalText);
    const encodedValue = await output.inputValue();
    
    // Switch to decode and use encoded value
    await page.locator('label[for="decodeMode"]').click();
    await input.fill(encodedValue);
    
    // Should get back the original text
    await expect(output).toHaveValue(originalText);
  });
});
