// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Unit Converter', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/tools/unit-converter');
  });

  test('page loads correctly', async ({ page }) => {
    await expect(page).toHaveTitle(/Unit|Einheit/i);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('all category buttons are visible', async ({ page }) => {
    const categories = [
      'cat-length', 'cat-mass', 'cat-temperature', 'cat-volume',
      'cat-time', 'cat-area', 'cat-speed', 'cat-acceleration',
      'cat-energy', 'cat-power', 'cat-pressure', 'cat-force',
      'cat-angle', 'cat-data'
    ];

    for (const catId of categories) {
      const label = page.locator(`label[for="${catId}"]`);
      await expect(label).toBeVisible();
    }
  });

  test('length category is selected by default', async ({ page }) => {
    await expect(page.locator('#cat-length')).toBeChecked();
  });

  test('input field accepts numbers', async ({ page }) => {
    const input = page.locator('#inputValue');
    
    await input.fill('123.45');
    await expect(input).toHaveValue('123.45');
    
    // Output should update
    const output = page.locator('#outputValue');
    await expect(output).not.toHaveText('-');
  });

  test('input field is type number', async ({ page }) => {
    const input = page.locator('#inputValue');
    await expect(input).toHaveAttribute('type', 'number');
  });

  test('unit dropdowns show correct units for length', async ({ page }) => {
    // Length should be default, check for typical length units
    const inputUnit = page.locator('#inputUnit1');
    
    // Check that common length units are present
    await expect(inputUnit.locator('option[value="m"]')).toBeAttached();
    await expect(inputUnit.locator('option[value="km"]')).toBeAttached();
    await expect(inputUnit.locator('option[value="ft"]')).toBeAttached();
    await expect(inputUnit.locator('option[value="mi"]')).toBeAttached();
  });

  test('switching to mass category updates unit dropdowns', async ({ page }) => {
    // Click on mass category
    await page.locator('label[for="cat-mass"]').click();
    
    await expect(page.locator('#cat-mass')).toBeChecked();
    
    const inputUnit = page.locator('#inputUnit1');
    
    // Check for mass units
    await expect(inputUnit.locator('option[value="g"]')).toBeAttached();
    await expect(inputUnit.locator('option[value="kg"]')).toBeAttached();
    await expect(inputUnit.locator('option[value="lb"]')).toBeAttached();
    
    // Length units should not be present
    await expect(inputUnit.locator('option[value="m"]')).not.toBeAttached();
  });

  test('switching to temperature category updates unit dropdowns', async ({ page }) => {
    await page.locator('label[for="cat-temperature"]').click();
    
    const inputUnit = page.locator('#inputUnit1');
    
    await expect(inputUnit.locator('option[value="C"]')).toBeAttached();
    await expect(inputUnit.locator('option[value="F"]')).toBeAttached();
    await expect(inputUnit.locator('option[value="K"]')).toBeAttached();
  });

  test('switching to data category updates unit dropdowns', async ({ page }) => {
    await page.locator('label[for="cat-data"]').click();
    
    const inputUnit = page.locator('#inputUnit1');
    
    await expect(inputUnit.locator('option[value="B"]')).toBeAttached();
    await expect(inputUnit.locator('option[value="KB"]')).toBeAttached();
    await expect(inputUnit.locator('option[value="MB"]')).toBeAttached();
    await expect(inputUnit.locator('option[value="GB"]')).toBeAttached();
  });

  test('speed category shows second unit dropdown for time', async ({ page }) => {
    await page.locator('label[for="cat-speed"]').click();
    
    // Second dropdowns should be visible for speed
    const inputUnit2 = page.locator('#inputUnit2');
    const outputUnit2 = page.locator('#outputUnit2');
    
    await expect(inputUnit2).toBeVisible();
    await expect(outputUnit2).toBeVisible();
    
    // Should have time units
    await expect(inputUnit2.locator('option[value="s"]')).toBeAttached();
    await expect(inputUnit2.locator('option[value="h"]')).toBeAttached();
  });

  test('acceleration category shows squared indicator', async ({ page }) => {
    await page.locator('label[for="cat-acceleration"]').click();
    
    // Square indicator should be visible
    const squareIndicator = page.locator('#squareIndicator');
    await expect(squareIndicator).toBeVisible();
    await expect(squareIndicator).toHaveText('²');
  });

  test('conversion table is populated', async ({ page }) => {
    const input = page.locator('#inputValue');
    await input.fill('100');
    
    // Wait for table to populate
    const tableBody = page.locator('#conversionTableBody');
    const rows = tableBody.locator('tr');
    
    // Should have multiple rows for different units
    await expect(rows).not.toHaveCount(0);
  });

  test('output value updates when input changes', async ({ page }) => {
    const input = page.locator('#inputValue');
    const output = page.locator('#outputValue');
    
    // Initial state
    await input.fill('1');
    const initialOutput = await output.textContent();
    
    // Change input
    await input.fill('1000');
    
    // Output should be different
    await expect(output).not.toHaveText(initialOutput || '-');
  });

  test('changing output unit updates the result', async ({ page }) => {
    const input = page.locator('#inputValue');
    const output = page.locator('#outputValue');
    const outputUnit = page.locator('#outputUnit1');
    
    await input.fill('1');
    
    // Select meters
    await outputUnit.selectOption('m');
    const meterOutput = await output.textContent();
    
    // Select kilometers
    await outputUnit.selectOption('km');
    const kmOutput = await output.textContent();
    
    // Results should be different
    expect(meterOutput).not.toBe(kmOutput);
  });

  test('privacy note is displayed', async ({ page }) => {
    // Look for privacy-related text in the SEO content
    const privacyNote = page.locator('text=/Privacy|Datenschutz|browser|Browser/i').first();
    await expect(privacyNote).toBeVisible();
  });

  test('disclaimer is displayed', async ({ page }) => {
    // Look for disclaimer text
    const disclaimer = page.locator('text=/Disclaimer|Haftungsausschluss|⚠️/i').first();
    await expect(disclaimer).toBeVisible();
  });

  test('all category buttons are clickable and switch categories', async ({ page }) => {
    const categories = [
      { id: 'cat-mass', unit: 'kg' },
      { id: 'cat-volume', unit: 'l' },
      { id: 'cat-time', unit: 's' },
      { id: 'cat-energy', unit: 'J' },
      { id: 'cat-data', unit: 'B' }
    ];

    for (const cat of categories) {
      await page.locator(`label[for="${cat.id}"]`).click();
      await expect(page.locator(`#${cat.id}`)).toBeChecked();
      
      const inputUnit = page.locator('#inputUnit1');
      await expect(inputUnit.locator(`option[value="${cat.unit}"]`)).toBeAttached();
    }
  });
});
