// @ts-check
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

test.describe('QR Code Generator', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/tools/qr-generator');
  });

  test('page loads correctly', async ({ page }) => {
    await expect(page).toHaveTitle(/QR|Code/i);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('generates QR code when clicking generate button', async ({ page }) => {
    // Enter some text
    const input = page.locator('#qrInput');
    await input.fill('https://lotsof.tools');
    
    // Click generate
    const generateBtn = page.locator('#generateBtn');
    await generateBtn.click();
    
    // Wait for download section to appear (indicates generation is complete)
    const downloadSection = page.locator('#downloadSection');
    await expect(downloadSection).toBeVisible();
    
    // Verify QR code image is visible
    await expect(page.locator('#qrCodeContainer img')).toBeVisible();
  });

  test('PNG export matches reference - URL 256px', async ({ page }) => {
    // Generate QR code with exact reference settings
    await page.locator('#qrInput').fill('https://lotsof.tools');
    await page.locator('#qrSize').selectOption('256');
    await page.locator('#generateBtn').click();
    
    // Wait for QR code to be generated
    await expect(page.locator('#downloadSection')).toBeVisible();
    
    // Download PNG
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#downloadPngBtn').click();
    const download = await downloadPromise;
    
    // Compare with reference file
    const downloadPath = await download.path();
    const referencePath = path.join(__dirname, '../../data/qr-reference-url-256.png');
    
    const downloadedFile = fs.readFileSync(downloadPath);
    const referenceFile = fs.readFileSync(referencePath);
    
    // Files should be identical
    expect(downloadedFile.equals(referenceFile)).toBe(true);
  });

  test('JPG export matches reference - URL 256px', async ({ page }) => {
    // Generate QR code with exact reference settings
    await page.locator('#qrInput').fill('https://lotsof.tools');
    await page.locator('#qrSize').selectOption('256');
    await page.locator('#generateBtn').click();
    
    // Wait for QR code to be generated
    await expect(page.locator('#downloadSection')).toBeVisible();
    
    // Download JPG
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#downloadJpgBtn').click();
    const download = await downloadPromise;
    
    // Compare with reference file
    const downloadPath = await download.path();
    const referencePath = path.join(__dirname, '../../data/qr-reference-url-256.jpg');
    
    const downloadedFile = fs.readFileSync(downloadPath);
    const referenceFile = fs.readFileSync(referencePath);
    
    // Files should be identical
    expect(downloadedFile.equals(referenceFile)).toBe(true);
  });

  test('SVG export matches reference - URL 256px', async ({ page }) => {
    // Generate QR code with exact reference settings
    await page.locator('#qrInput').fill('https://lotsof.tools');
    await page.locator('#qrSize').selectOption('256');
    await page.locator('#generateBtn').click();
    
    // Wait for QR code to be generated
    await expect(page.locator('#downloadSection')).toBeVisible();
    
    // Download SVG
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#downloadSvgBtn').click();
    const download = await downloadPromise;
    
    // Compare with reference file
    const downloadPath = await download.path();
    const referencePath = path.join(__dirname, '../../data/qr-reference-url-256.svg');
    
    const downloadedContent = fs.readFileSync(downloadPath, 'utf-8');
    const referenceContent = fs.readFileSync(referencePath, 'utf-8');
    
    // Normalize whitespace (remove extra newlines) before comparison
    const normalizeWhitespace = (str) => str.replace(/\n\s*\n/g, '\n').trim();
    expect(normalizeWhitespace(downloadedContent)).toBe(normalizeWhitespace(referenceContent));
  });

  test('Text QR Code 512px - PNG export matches reference', async ({ page }) => {
    // Generate QR code with exact reference settings
    await page.locator('#qrType').selectOption('text');
    await page.waitForTimeout(100); // Wait for input fields to update
    await page.locator('#qrInput').fill('Test QR Code');
    await page.locator('#qrSize').selectOption('512');
    await page.locator('#generateBtn').click();
    
    // Wait for QR code to be generated
    await expect(page.locator('#downloadSection')).toBeVisible();
    
    // Download PNG
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#downloadPngBtn').click();
    const download = await downloadPromise;
    
    // Compare with reference file
    const downloadPath = await download.path();
    const referencePath = path.join(__dirname, '../../data/qr-reference-text-512.png');
    
    const downloadedFile = fs.readFileSync(downloadPath);
    const referenceFile = fs.readFileSync(referencePath);
    
    // Files should be identical
    expect(downloadedFile.equals(referenceFile)).toBe(true);
  });

  test('Text QR Code 512px - SVG export matches reference', async ({ page }) => {
    // Generate QR code with exact reference settings
    await page.locator('#qrType').selectOption('text');
    await page.waitForTimeout(100);
    await page.locator('#qrInput').fill('Test QR Code');
    await page.locator('#qrSize').selectOption('512');
    await page.locator('#generateBtn').click();
    
    // Wait for QR code to be generated
    await expect(page.locator('#downloadSection')).toBeVisible();
    
    // Download SVG
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#downloadSvgBtn').click();
    const download = await downloadPromise;
    
    // Compare with reference file
    const downloadPath = await download.path();
    const referencePath = path.join(__dirname, '../../data/qr-reference-text-512.svg');
    
    const downloadedContent = fs.readFileSync(downloadPath, 'utf-8');
    const referenceContent = fs.readFileSync(referencePath, 'utf-8');
    
    // Normalize whitespace (remove extra newlines) before comparison
    const normalizeWhitespace = (str) => str.replace(/\n\s*\n/g, '\n').trim();
    expect(normalizeWhitespace(downloadedContent)).toBe(normalizeWhitespace(referenceContent));
  });

  test('Custom colors - PNG export matches reference', async ({ page }) => {
    // Set custom colors
    await page.locator('#colorDark').fill('#ff0000');
    await page.locator('#colorLight').fill('#0000ff');
    
    // Generate QR code
    await page.locator('#qrInput').fill('https://example.com');
    await page.locator('#qrSize').selectOption('256');
    await page.locator('#generateBtn').click();
    
    // Wait for QR code to be generated
    await expect(page.locator('#downloadSection')).toBeVisible();
    
    // Download PNG
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#downloadPngBtn').click();
    const download = await downloadPromise;
    
    // Compare with reference file
    const downloadPath = await download.path();
    const referencePath = path.join(__dirname, '../../data/qr-reference-colors-256.png');
    
    const downloadedFile = fs.readFileSync(downloadPath);
    const referenceFile = fs.readFileSync(referencePath);
    
    // Files should be identical
    expect(downloadedFile.equals(referenceFile)).toBe(true);
  });

  test('Custom colors - SVG export matches reference', async ({ page }) => {
    // Set custom colors
    await page.locator('#colorDark').fill('#ff0000');
    await page.locator('#colorLight').fill('#0000ff');
    
    // Generate QR code
    await page.locator('#qrInput').fill('https://example.com');
    await page.locator('#qrSize').selectOption('256');
    await page.locator('#generateBtn').click();
    
    // Wait for QR code to be generated
    await expect(page.locator('#downloadSection')).toBeVisible();
    
    // Download SVG
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#downloadSvgBtn').click();
    const download = await downloadPromise;
    
    // Compare with reference file
    const downloadPath = await download.path();
    const referencePath = path.join(__dirname, '../../data/qr-reference-colors-256.svg');
    
    const downloadedContent = fs.readFileSync(downloadPath, 'utf-8');
    const referenceContent = fs.readFileSync(referencePath, 'utf-8');
    
    // Normalize whitespace (remove extra newlines) before comparison
    const normalizeWhitespace = (str) => str.replace(/\n\s*\n/g, '\n').trim();
    expect(normalizeWhitespace(downloadedContent)).toBe(normalizeWhitespace(referenceContent));
  });

  test('different QR types work', async ({ page }) => {
    const types = [
      { value: 'url', input: '#qrInput', data: 'https://example.com' },
      { value: 'email', input: '#emailAddr', data: 'test@example.com' },
      { value: 'phone', input: '#phoneNumber', data: '+1234567890' },
      { value: 'sms', input: '#smsNumber', data: '+1234567890' }
    ];
    
    for (const type of types) {
      // Select type
      await page.locator('#qrType').selectOption(type.value);
      
      // Wait for input fields to update
      await page.waitForTimeout(100);
      
      // Fill in data
      await page.locator(type.input).fill(type.data);
      
      // Generate
      await page.locator('#generateBtn').click();
      
      // Wait for generation to complete
      await expect(page.locator('#downloadSection')).toBeVisible();
      
      // Verify QR code appears (check the image which is the visible output)
      await expect(page.locator('#qrCodeContainer img')).toBeVisible();
      
      // Clear for next iteration
      await page.locator('#qrCodeContainer').evaluate(el => el.innerHTML = '');
    }
  });

  test('custom size works', async ({ page }) => {
    // Select custom size
    await page.locator('#qrSize').selectOption('custom');
    
    // Custom size fields should appear
    await expect(page.locator('#customSizeFields')).toBeVisible();
    
    // Set custom size
    await page.locator('#qrWidth').fill('500');
    await page.locator('#qrHeight').fill('500');
    
    // Generate QR code
    await page.locator('#qrInput').fill('Custom Size Test');
    await page.locator('#generateBtn').click();
    
    // Wait for generation to complete
    await expect(page.locator('#downloadSection')).toBeVisible();
    
    // Verify canvas has correct size
    const canvas = page.locator('#qrCodeContainer canvas');
    await expect(canvas).toBeAttached();
    
    const width = await canvas.evaluate((el) => /** @type {HTMLCanvasElement} */ (el).width);
    const height = await canvas.evaluate((el) => /** @type {HTMLCanvasElement} */ (el).height);
    
    expect(width).toBe(500);
    expect(height).toBe(500);
  });
});
