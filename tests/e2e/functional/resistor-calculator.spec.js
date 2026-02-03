const { test, expect } = require('@playwright/test');

test.describe('Resistor Calculator', () => {
  test('tolerance toggle should be visible and functional for 3-band resistors', async ({ page }) => {
    // Navigate to resistor calculator
    await page.goto('/tools/resistor-calculator');
    
    // Select 3-band mode
    const band3Label = page.locator('label[for="band3"]');
    await band3Label.click();
    
    // Wait a moment for JavaScript to update the UI
    await page.waitForTimeout(100);
    
    // Wait for and verify the tolerance toggle container is visible in results area
    const toleranceToggleContainer = page.locator('#defaultToleranceContainer');
    await expect(toleranceToggleContainer).toBeVisible({ timeout: 5000 });
    
    // Verify the IEC tolerance checkbox exists and is unchecked by default
    const iecCheckbox = page.locator('#iecTolerance');
    await expect(iecCheckbox).toBeVisible();
    await expect(iecCheckbox).not.toBeChecked();
    
    // Verify tolerance shows 5% when checkbox is unchecked
    const toleranceValue = page.locator('#toleranceValue');
    await expect(toleranceValue).toContainText('±5%');
    
    // Toggle the checkbox on
    await iecCheckbox.click();
    await expect(iecCheckbox).toBeChecked();
    
    // Verify tolerance changes to 20% when checked
    await expect(toleranceValue).toContainText('±20%');
    
    // Toggle back off
    await iecCheckbox.click();
    await expect(iecCheckbox).not.toBeChecked();
    await expect(toleranceValue).toContainText('±5%');
  });

  test('tolerance toggle should be hidden for 4-band resistors', async ({ page }) => {
    await page.goto('/tools/resistor-calculator');
    
    // Default is 4-band, verify toggle is hidden
    const toleranceToggleContainer = page.locator('#defaultToleranceContainer');
    await expect(toleranceToggleContainer).toBeHidden();
    
    // Select 5-band and verify toggle is still hidden
    await page.locator('label[for="band5"]').click();
    await expect(toleranceToggleContainer).toBeHidden();
    
    // Select 6-band and verify toggle is still hidden
    await page.locator('label[for="band6"]').click();
    await expect(toleranceToggleContainer).toBeHidden();
  });

  test('tolerance toggle state should persist in URL', async ({ page }) => {
    await page.goto('/tools/resistor-calculator');
    
    // Select 3-band mode
    await page.locator('label[for="band3"]').click();
    
    // Check the IEC checkbox (from default unchecked)
    const iecCheckbox = page.locator('#iecTolerance');
    await iecCheckbox.click();
    
    // Verify URL contains iec=1
    await expect(page).toHaveURL(/iec=1/);
    
    // Reload the page with the URL parameter
    const currentUrl = page.url();
    await page.goto(currentUrl);
    
    // Verify checkbox state persisted
    await expect(page.locator('#iecTolerance')).toBeChecked();
    await expect(page.locator('#toleranceValue')).toContainText('±20%');
  });
});
