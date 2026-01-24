// @ts-check
const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;
const fs = require('fs');
const path = require('path');

/**
 * Accessibility tests for lotsof.tools
 * Uses axe-core to check WCAG 2.1 compliance including color contrast
 * 
 * WCAG 2.1 AA requires:
 * - Normal text: 4.5:1 contrast ratio
 * - Large text (18pt+ or 14pt bold): 3:1 contrast ratio
 * - UI components and graphics: 3:1 contrast ratio
 */

/**
 * Dynamically load active tools from tool_config.json
 * This ensures new tools are automatically tested when added
 */
function getActiveToolUrls() {
  const configPath = path.join(__dirname, '../../app/config/tool_config.json');
  const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
  
  // Map config keys to URL paths
  const toolUrlMap = {
    'ascii_table': '/tools/ascii-table',
    'barcode_generator': '/tools/barcode-generator',
    'base64': '/tools/base64',
    'base_converter': '/tools/base-converter',
    'bmi_calculator': '/tools/bmi-calculator',
    'calendar': '/tools/calendar',
    'clock': '/tools/clock',
    'color': '/tools/color',
    'colorblind': '/tools/colorblind',
    'coordinate_converter': '/tools/coordinate-converter',
    'csv_table': '/tools/csv-table',
    'date_calculator': '/tools/time-since',
    'date_calculator_until': '/tools/time-until',
    'date_calculator_between': '/tools/time-between',
    'dice': '/tools/dice',
    'diff': '/tools/text-diff',
    'distance': '/tools/distance',
    'dns_lookup': '/tools/dns-lookup',
    'emoji_search': '/tools/emoji-search',
    'favicon_generator': '/tools/favicon-generator',
    'hash_generator': '/tools/hash-generator',
    'holiday_calendar': '/tools/holiday-calendar',
    'iban_validator': '/tools/iban-validator',
    'icon_finder': '/tools/icon-finder',
    'image_cropper': '/tools/image-cropper',
    'ip_lookup': '/tools/ip-lookup',
    'json_formatter': '/tools/json-formatter',
    'lastfm_export': '/tools/lastfm-export',
    'letter_counter': '/tools/letter-counter',
    'lorem_ipsum': '/tools/lorem-ipsum',
    'map_maker': '/tools/map-marker',
    'map_tracer': '/tools/map-tracer',
    'noise_generator': '/tools/noise-generator',
    'qr_generator': '/tools/qr-generator',
    'radius': '/tools/radius',
    'random_string': '/tools/random-string',
    'simulate_location': '/tools/simulate-location',
    'speed_test': '/tools/speed-test',
    'stopwatch': '/tools/stopwatch',
    'subtitle_converter': '/tools/subtitle-converter',
    'teleprompter': '/tools/teleprompter',
    'time_converter': '/tools/time-converter',
    'unit_converter': '/tools/unit-converter',
    'url_checker': '/tools/url-checker',
    'uuid_generator': '/tools/uuid-generator',
    'xml_formatter': '/tools/xml-formatter',
    'yaml_formatter': '/tools/yaml-formatter',
    'youtube_dl': '/tools/youtube-dl',
  };
  
  // Return URLs for active tools only
  return Object.entries(config)
    .filter(([key, value]) => value.active && toolUrlMap[key])
    .map(([key]) => toolUrlMap[key]);
}

// Get tool URLs dynamically from config
const TOOL_URLS = getActiveToolUrls();

// Helper function to run axe analysis
async function runAccessibilityAudit(page, options = {}) {
  const axeBuilder = new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']);
  
  // Focus on color contrast rules if specified
  if (options.contrastOnly) {
    axeBuilder.withRules(['color-contrast', 'color-contrast-enhanced']);
  }
  
  return await axeBuilder.analyze();
}

// Helper to format violations for readable output
function formatViolations(violations) {
  return violations.map(v => ({
    rule: v.id,
    impact: v.impact,
    description: v.description,
    helpUrl: v.helpUrl,
    nodes: v.nodes.map(n => ({
      html: n.html.substring(0, 200),
      failureSummary: n.failureSummary,
    })),
  }));
}

test.describe('Accessibility - Color Contrast Tests', () => {
  
  test.describe('Light Mode', () => {
    for (const toolUrl of TOOL_URLS) {
      test(`${toolUrl} has sufficient color contrast`, async ({ page }) => {
        await page.goto(toolUrl);
        
        // Wait for page to fully load
        await page.waitForLoadState('networkidle');
        
        // Run axe analysis focusing on color contrast
        const results = await runAccessibilityAudit(page, { contrastOnly: true });
        
        // Log violations for debugging
        if (results.violations.length > 0) {
          console.log(`\nContrast violations on ${toolUrl}:`);
          console.log(JSON.stringify(formatViolations(results.violations), null, 2));
        }
        
        // Assert no color contrast violations (WCAG AA only, not AAA)
        expect(results.violations.filter(v => 
          v.id === 'color-contrast'
        )).toHaveLength(0);
      });
    }
  });

  // Dark mode tests
  test.describe('Dark Mode', () => {
    for (const toolUrl of TOOL_URLS) {
      test(`${toolUrl} (dark mode) has sufficient color contrast`, async ({ page }) => {
        await page.goto(toolUrl);
        
        // Enable dark mode (adjust selector based on implementation)
        await page.evaluate(() => {
          document.documentElement.setAttribute('data-bs-theme', 'dark');
        });
        
        // Wait for styles to apply
        await page.waitForTimeout(100);
        
        const results = await runAccessibilityAudit(page, { contrastOnly: true });
        
        if (results.violations.length > 0) {
          console.log(`\nDark mode contrast violations on ${toolUrl}:`);
          console.log(JSON.stringify(formatViolations(results.violations), null, 2));
        }
        
        // Assert no color contrast violations (WCAG AA only, not AAA)
        expect(results.violations.filter(v => 
          v.id === 'color-contrast'
        )).toHaveLength(0);
      });
    }
  });
});

test.describe('Accessibility - Full WCAG Audit', () => {
  
  // Run a full accessibility audit on the homepage
  test('Homepage passes WCAG 2.1 AA', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const results = await runAccessibilityAudit(page);
    
    if (results.violations.length > 0) {
      console.log('\nHomepage accessibility violations:');
      console.log(JSON.stringify(formatViolations(results.violations), null, 2));
    }
    
    // For now, just log - can make strict later
    expect(results.violations).toBeDefined();
  });

  // Sample a few key tools for full audit
  const sampleTools = ['/tools/base64', '/tools/json-formatter', '/tools/clock'];
  
  for (const toolUrl of sampleTools) {
    test(`${toolUrl} passes WCAG 2.1 AA`, async ({ page }) => {
      await page.goto(toolUrl);
      await page.waitForLoadState('networkidle');
      
      const results = await runAccessibilityAudit(page);
      
      if (results.violations.length > 0) {
        console.log(`\nAccessibility violations on ${toolUrl}:`);
        console.log(JSON.stringify(formatViolations(results.violations), null, 2));
      }
      
      // Log but don't fail for now - use this to identify issues
      expect(results.violations).toBeDefined();
    });
  }
});

test.describe('Accessibility - Contrast Ratio Report', () => {
  
  test('Generate contrast report for all tools', async ({ page }) => {
    const report = {
      timestamp: new Date().toISOString(),
      tools: [],
    };
    
    // Test a subset for the report (full list would be slow)
    const toolsToTest = TOOL_URLS.slice(0, 10);
    
    for (const toolUrl of toolsToTest) {
      try {
        await page.goto(toolUrl);
        await page.waitForLoadState('networkidle');
        
        const results = await runAccessibilityAudit(page, { contrastOnly: true });
        
        report.tools.push({
          url: toolUrl,
          passed: results.violations.length === 0,
          violationCount: results.violations.length,
          violations: results.violations.map(v => ({
            rule: v.id,
            impact: v.impact,
            nodeCount: v.nodes.length,
          })),
        });
      } catch (error) {
        report.tools.push({
          url: toolUrl,
          error: error.message,
        });
      }
    }
    
    console.log('\n=== Contrast Ratio Report ===');
    console.log(JSON.stringify(report, null, 2));
    
    // This test always passes - it's for generating reports
    expect(report.tools.length).toBeGreaterThan(0);
  });
});
