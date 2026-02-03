const { test, expect } = require('@playwright/test');

test.describe('Resistor Calculator', () => {
  test('tolerance toggle should be visible and functional for 3-band resistors', async ({ page }) => {
    // Navigate to resistor calculator
    await page.goto('/tools/resistor-calculator');
    
    // Select 3-band mode
    const band3Radio = page.locator('input[name="bandCount"][value="3"]');
    await band3Radio.click();
    
    // Verify the tolerance toggle container is visible
    const toleranceToggleContainer = page.locator('#defaultToleranceContainer');
    await expect(toleranceToggleContainer).toBeVisible();
    
    // Verify the IEC tolerance checkbox exists and is checked by default
    const iecCheckbox = page.locator('#iecTolerance');
    await expect(iecCheckbox).toBeVisible();
    await expect(iecCheckbox).toBeChecked();
    
    // Verify tolerance shows 20% when checkbox is checked
    const toleranceValue = page.locator('#toleranceValue');
    await expect(toleranceValue).toContainText('±20%');
    
    // Toggle the checkbox off
    await iecCheckbox.click();
    await expect(iecCheckbox).not.toBeChecked();
    
    // Verify tolerance changes to 5% when unchecked
    await expect(toleranceValue).toContainText('±5%');
    
    // Toggle back on
    await iecCheckbox.click();
    await expect(iecCheckbox).toBeChecked();
    await expect(toleranceValue).toContainText('±20%');
  });

  test('tolerance toggle should be hidden for 4-band resistors', async ({ page }) => {
    await page.goto('/tools/resistor-calculator');
    
    // Default is 4-band, verify toggle is hidden
    const toleranceToggleContainer = page.locator('#defaultToleranceContainer');
    await expect(toleranceToggleContainer).toBeHidden();
    
    // Select 5-band and verify toggle is still hidden
    await page.locator('input[name="bandCount"][value="5"]').click();
    await expect(toleranceToggleContainer).toBeHidden();
    
    // Select 6-band and verify toggle is still hidden
    await page.locator('input[name="bandCount"][value="6"]').click();
    await expect(toleranceToggleContainer).toBeHidden();
  });

  test('tolerance toggle state should persist in URL', async ({ page }) => {
    await page.goto('/tools/resistor-calculator');
    
    // Select 3-band mode
    await page.locator('input[name="bandCount"][value="3"]').click();
    
    // Uncheck the IEC checkbox
    const iecCheckbox = page.locator('#iecTolerance');
    await iecCheckbox.click();
    
    // Verify URL contains iec=0
    await expect(page).toHaveURL(/iec=0/);
    
    // Reload the page with the URL parameter
    const currentUrl = page.url();
    await page.goto(currentUrl);
    
    // Verify checkbox state persisted
    await expect(page.locator('#iecTolerance')).not.toBeChecked();
    await expect(page.locator('#toleranceValue')).toContainText('±5%');
  });
});
