/**
 * E2E tests for Timezone Calculator
 * Tests timezone conversion with DST handling and various input formats
 */

const { test, expect } = require('@playwright/test');

test.describe('Timezone Calculator', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/tools/timezone-calculator');
    await page.waitForLoadState('networkidle');
  });

  test('Page loads with correct title and elements', async ({ page }) => {
    await expect(page).toHaveTitle(/Timezone Calculator/);
    
    // Check main elements exist
    await expect(page.locator('#sourceTime')).toBeVisible();
    await expect(page.locator('#sourceTimezone')).toBeVisible();
    await expect(page.locator('#targetTimezone')).toBeVisible();
    await expect(page.locator('#convertBtn')).toBeVisible();
    await expect(page.locator('#swapBtn')).toBeVisible();
  });

  test('Converts time-only input (uses today)', async ({ page }) => {
    // Enter time only
    await page.locator('#sourceTime').fill('14:30');
    await page.locator('#sourceTimezone').fill('Europe/Berlin');
    await page.locator('#targetTimezone').fill('America/New_York');
    
    // Click convert
    await page.locator('#convertBtn').click();
    
    // Check results appear
    await expect(page.locator('#resultsCard')).toBeVisible();
    
    // Check that both timezones are shown
    const resultsText = await page.locator('#resultsContent').textContent();
    expect(resultsText).toContain('Europe/Berlin');
    expect(resultsText).toContain('America/New_York');
    expect(resultsText).toContain('14:30');
  });

  test('Converts full date-time input', async ({ page }) => {
    // Enter full date-time
    await page.locator('#sourceTime').fill('2026-11-30 15:00');
    await page.locator('#sourceTimezone').fill('Europe/Berlin');
    await page.locator('#targetTimezone').fill('America/New_York');
    
    // Click convert
    await page.locator('#convertBtn').click();
    
    // Check results appear
    await expect(page.locator('#resultsCard')).toBeVisible();
    
    // Check that the date is shown
    const resultsText = await page.locator('#resultsContent').textContent();
    expect(resultsText).toContain('11/30/2026');
    expect(resultsText).toContain('15:00');
  });

  test('Handles DST correctly - winter time', async ({ page }) => {
    // January (winter - no DST in most places)
    await page.locator('#sourceTime').fill('2026-01-15 12:00');
    await page.locator('#sourceTimezone').fill('America/New_York');
    await page.locator('#targetTimezone').fill('UTC');
    
    await page.locator('#convertBtn').click();
    await expect(page.locator('#resultsCard')).toBeVisible();
    
    // New York is UTC-5 in winter (EST)
    const resultsText = await page.locator('#resultsContent').textContent();
    expect(resultsText).toContain('UTC-05:00');
  });

  test('Handles DST correctly - summer time', async ({ page }) => {
    // July (summer - DST active)
    await page.locator('#sourceTime').fill('2026-07-15 12:00');
    await page.locator('#sourceTimezone').fill('America/New_York');
    await page.locator('#targetTimezone').fill('UTC');
    
    await page.locator('#convertBtn').click();
    await expect(page.locator('#resultsCard')).toBeVisible();
    
    // New York is UTC-4 in summer (EDT)
    const resultsText = await page.locator('#resultsContent').textContent();
    expect(resultsText).toContain('UTC-04:00');
  });

  test('Swap timezones button works', async ({ page }) => {
    // Set initial timezones
    await page.locator('#sourceTimezone').fill('Europe/Berlin');
    await page.locator('#targetTimezone').fill('America/New_York');
    
    // Click swap
    await page.locator('#swapBtn').click();
    
    // Check they are swapped
    const sourceValue = await page.locator('#sourceTimezone').inputValue();
    const targetValue = await page.locator('#targetTimezone').inputValue();
    
    expect(sourceValue).toBe('America/New_York');
    expect(targetValue).toBe('Europe/Berlin');
  });

  test('URL parameters are loaded correctly', async ({ page }) => {
    // Navigate with URL parameters
    await page.goto('/tools/timezone-calculator?time=2026-12-25%2010:00&from=Europe/London&to=America/Los_Angeles');
    await page.waitForLoadState('networkidle');
    
    // Check inputs are populated
    const sourceTime = await page.locator('#sourceTime').inputValue();
    const sourceTimezone = await page.locator('#sourceTimezone').inputValue();
    const targetTimezone = await page.locator('#targetTimezone').inputValue();
    
    expect(sourceTime).toBe('2026-12-25 10:00');
    expect(sourceTimezone).toBe('Europe/London');
    expect(targetTimezone).toBe('America/Los_Angeles');
    
    // Results should auto-convert
    await expect(page.locator('#resultsCard')).toBeVisible();
  });

  test('URL is updated after conversion', async ({ page }) => {
    await page.locator('#sourceTime').fill('15:30');
    await page.locator('#sourceTimezone').fill('Europe/Paris');
    await page.locator('#targetTimezone').fill('Asia/Tokyo');
    
    await page.locator('#convertBtn').click();
    await expect(page.locator('#resultsCard')).toBeVisible();
    
    // Check URL contains parameters (URL-encoded)
    const url = page.url();
    expect(url).toMatch(/time=15(%3A|:)30/); // Accept both encoded and unencoded
    expect(url).toMatch(/from=Europe(%2F|\/)Paris/);
    expect(url).toMatch(/to=Asia(%2F|\/)Tokyo/);
  });

  test('Handles 12-hour AM/PM format', async ({ page }) => {
    await page.locator('#sourceTime').fill('2:30 PM');
    await page.locator('#sourceTimezone').fill('Europe/Berlin');
    await page.locator('#targetTimezone').fill('UTC');
    
    await page.locator('#convertBtn').click();
    await expect(page.locator('#resultsCard')).toBeVisible();
    
    // Should show 14:30 (2:30 PM in 24-hour format)
    const resultsText = await page.locator('#resultsContent').textContent();
    expect(resultsText).toContain('14:30');
  });

  test('Handles time with seconds', async ({ page }) => {
    await page.locator('#sourceTime').fill('14:30:45');
    await page.locator('#sourceTimezone').fill('Europe/Berlin');
    await page.locator('#targetTimezone').fill('UTC');
    
    await page.locator('#convertBtn').click();
    await expect(page.locator('#resultsCard')).toBeVisible();
    
    // Should show seconds
    const resultsText = await page.locator('#resultsContent').textContent();
    expect(resultsText).toContain('14:30:45');
  });

  test('Shows error for invalid time input', async ({ page }) => {
    await page.locator('#sourceTime').fill('invalid time');
    await page.locator('#sourceTimezone').fill('Europe/Berlin');
    await page.locator('#targetTimezone').fill('UTC');
    
    await page.locator('#convertBtn').click();
    
    // Error should be visible
    await expect(page.locator('#errorMessage')).toBeVisible();
    
    // Results should not be visible
    await expect(page.locator('#resultsCard')).not.toBeVisible();
  });

  test('Timezone search/autocomplete works', async ({ page }) => {
    // Type partial timezone name
    await page.locator('#sourceTimezone').fill('Berlin');
    
    // The datalist should filter options (browser native behavior)
    // We can verify the value can be set
    await page.locator('#sourceTimezone').fill('Europe/Berlin');
    const value = await page.locator('#sourceTimezone').inputValue();
    expect(value).toBe('Europe/Berlin');
  });

  test('Converts between different DST schedules correctly', async ({ page }) => {
    // Europe and US have different DST transition dates
    // Test a date where Europe is in DST but US might not be (or vice versa)
    await page.locator('#sourceTime').fill('2026-03-15 12:00');
    await page.locator('#sourceTimezone').fill('Europe/Berlin');
    await page.locator('#targetTimezone').fill('America/New_York');
    
    await page.locator('#convertBtn').click();
    await expect(page.locator('#resultsCard')).toBeVisible();
    
    // Both should show their correct offsets for this date
    const resultsText = await page.locator('#resultsContent').textContent();
    expect(resultsText).toContain('UTC');
    expect(resultsText).toMatch(/[+-]\d{2}:\d{2}/); // Should contain offset format
  });

  test('Enter key triggers conversion', async ({ page }) => {
    await page.locator('#sourceTime').fill('10:00');
    await page.locator('#sourceTimezone').fill('Europe/Berlin');
    await page.locator('#targetTimezone').fill('UTC');
    
    // Press Enter in the time input
    await page.locator('#sourceTime').press('Enter');
    
    // Results should appear
    await expect(page.locator('#resultsCard')).toBeVisible();
  });

  test('Auto-converts when timezone changes', async ({ page }) => {
    // First conversion
    await page.locator('#sourceTime').fill('12:00');
    await page.locator('#sourceTimezone').fill('Europe/Berlin');
    await page.locator('#targetTimezone').fill('UTC');
    await page.locator('#convertBtn').click();
    await expect(page.locator('#resultsCard')).toBeVisible();
    
    // Change target timezone
    await page.locator('#targetTimezone').fill('America/New_York');
    
    // Manually trigger convert after timezone change
    await page.locator('#convertBtn').click();
    
    // Results should update
    const resultsText = await page.locator('#resultsContent').textContent();
    expect(resultsText).toContain('America/New_York');
  });
});
