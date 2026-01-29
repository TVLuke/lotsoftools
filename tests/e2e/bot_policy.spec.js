const { test, expect } = require('@playwright/test');

test.describe('Bot Policy Honeypot', () => {
  test('bot-policy link should be accessible and return correct content', async ({ page }) => {
    // Navigate to bot-policy page
    await page.goto('/bot-policy');
    
    // Check that the page loads successfully
    await expect(page).toHaveTitle(/Lots of Tools/);
    
    // Check for the main heading
    const heading = page.locator('h2');
    await expect(heading).toContainText('Bot-Policy');
    
    // Check for the robot icon
    const robotIcon = page.locator('.fa-robot');
    await expect(robotIcon).toBeVisible();
    
    // Check for welcome message
    const welcomeText = page.locator('h3');
    await expect(welcomeText).toContainText('Welcome to Lots of Tools!');
    
    // Check for guidelines
    const guidelines = page.locator('ul li');
    await expect(guidelines).toHaveCount(3); // Should have 3 guidelines
    
    // Check for specific guidelines
    await expect(page.locator('text=Don\'t generate excessive traffic')).toBeVisible();
    await expect(page.locator('text=Crawl our pages at reasonable intervals')).toBeVisible();
    await expect(page.locator('text=Use a descriptive User-Agent')).toBeVisible();
    
    // Check for back to home button
    const backButton = page.locator('a[href="/"]');
    await expect(backButton).toContainText('Back to Home');
    await expect(backButton).toBeVisible();
    
    // Check that it's a honeypot (should be hidden from real users)
    // We can't test JavaScript hiding in this context, but we can verify the link exists
    const response = await page.goto('/bot-policy');
    expect(response.status()).toBe(200);
  });
  
  test('bot-policy link should be hidden from real users with JavaScript', async ({ page }) => {
    // Enable JavaScript
    await page.goto('/bot-policy');
    
    // Check that the bot-policy link in footer is hidden
    const botPolicyLink = page.locator('#bot-policy-link');
    await expect(botPolicyLink).toHaveCSS('display', 'none');
  });
  
  test('bot-policy link should be visible without JavaScript', async ({ context }) => {
    // Create a new context with JavaScript disabled
    const contextOptions = {
      javaScriptEnabled: false
    };
    const noJSContext = await context.newContext(contextOptions);
    const page = await noJSContext.newPage();
    
    // Navigate to home page
    await page.goto('/');
    
    // Check that the bot-policy link is visible without JavaScript
    const botPolicyLink = page.locator('#bot-policy-link');
    await expect(botPolicyLink).toBeVisible();
    await expect(botPolicyLink).toContainText('Bot-Policy');
    
    // Click the link and verify it works
    await botPolicyLink.click();
    await expect(page).toHaveURL(/.*bot-policy/);
    
    await page.close();
    await noJSContext.close();
  });
});
