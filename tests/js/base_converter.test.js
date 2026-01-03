/**
 * Tests for Base Converter Library
 * Run with: node tests/js/base_converter.test.js
 */

const BaseConverter = require('../../app/static/js/base_converter.js');

let passed = 0;
let failed = 0;

function test(name, fn) {
    try {
        fn();
        console.log(`✓ ${name}`);
        passed++;
    } catch (e) {
        console.log(`✗ ${name}`);
        console.log(`  Error: ${e.message}`);
        failed++;
    }
}

function assertEqual(actual, expected, msg = '') {
    // Handle BigInt comparison
    if (typeof actual === 'bigint' || typeof expected === 'bigint') {
        if (actual !== expected) {
            throw new Error(`${msg}\n  Expected: ${expected}\n  Actual: ${actual}`);
        }
        return;
    }
    const actualStr = JSON.stringify(actual);
    const expectedStr = JSON.stringify(expected);
    if (actualStr !== expectedStr) {
        throw new Error(`${msg}\n  Expected: ${expectedStr}\n  Actual: ${actualStr}`);
    }
}

function assertNull(actual, msg = '') {
    if (actual !== null) {
        throw new Error(`${msg}\n  Expected null, got: ${JSON.stringify(actual)}`);
    }
}

function assertNotNull(actual, msg = '') {
    if (actual === null) {
        throw new Error(`${msg}\n  Expected non-null value, got null`);
    }
}

console.log('=== Base Converter Tests ===\n');

// Test: getDefaultSymbols
console.log('--- getDefaultSymbols ---');

test('getDefaultSymbols(2) returns binary symbols', () => {
    const symbols = BaseConverter.getDefaultSymbols(2);
    assertEqual(symbols, ['0', '1']);
});

test('getDefaultSymbols(8) returns octal symbols', () => {
    const symbols = BaseConverter.getDefaultSymbols(8);
    assertEqual(symbols, ['0', '1', '2', '3', '4', '5', '6', '7']);
});

test('getDefaultSymbols(10) returns decimal symbols', () => {
    const symbols = BaseConverter.getDefaultSymbols(10);
    assertEqual(symbols, ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']);
});

test('getDefaultSymbols(16) returns hex symbols', () => {
    const symbols = BaseConverter.getDefaultSymbols(16);
    assertEqual(symbols.length, 16);
    assertEqual(symbols[15], 'F');
});

test('getDefaultSymbols(36) includes A-Z', () => {
    const symbols = BaseConverter.getDefaultSymbols(36);
    assertEqual(symbols.length, 36);
    assertEqual(symbols[10], 'A');
    assertEqual(symbols[35], 'Z');
});

test('getDefaultSymbols(60) includes Greek letters', () => {
    const symbols = BaseConverter.getDefaultSymbols(60);
    assertEqual(symbols.length, 60);
    assertEqual(symbols[36], 'α'); // First Greek letter after 0-9 (10) and A-Z (26)
});

// Test: validateSymbols
console.log('\n--- validateSymbols ---');

test('validateSymbols accepts valid symbols', () => {
    const result = BaseConverter.validateSymbols(['0', '1'], 2);
    assertEqual(result.valid, true);
    assertNull(result.error);
});

test('validateSymbols rejects wrong count', () => {
    const result = BaseConverter.validateSymbols(['0', '1', '2'], 2);
    assertEqual(result.valid, false);
    assertNotNull(result.error);
});

test('validateSymbols rejects duplicates', () => {
    const result = BaseConverter.validateSymbols(['0', '0'], 2);
    assertEqual(result.valid, false);
    assertNotNull(result.error);
});

test('validateSymbols rejects case-insensitive duplicates', () => {
    const result = BaseConverter.validateSymbols(['a', 'A'], 2);
    assertEqual(result.valid, false);
    assertNotNull(result.error);
});

test('validateSymbols rejects empty symbols', () => {
    const result = BaseConverter.validateSymbols(['0', ''], 2);
    assertEqual(result.valid, false);
    assertNotNull(result.error);
});

// Test: toDecimal
console.log('\n--- toDecimal ---');

test('toDecimal converts binary 1010 to 10', () => {
    const result = BaseConverter.toDecimal('1010', 2, ['0', '1']);
    assertEqual(result.value, 10n);
    assertNull(result.error);
});

test('toDecimal converts binary 11111111 to 255', () => {
    const result = BaseConverter.toDecimal('11111111', 2, ['0', '1']);
    assertEqual(result.value, 255n);
});

test('toDecimal converts hex FF to 255', () => {
    const symbols = BaseConverter.getDefaultSymbols(16);
    const result = BaseConverter.toDecimal('FF', 16, symbols);
    assertEqual(result.value, 255n);
});

test('toDecimal converts hex ff (lowercase) to 255', () => {
    const symbols = BaseConverter.getDefaultSymbols(16);
    const result = BaseConverter.toDecimal('ff', 16, symbols);
    assertEqual(result.value, 255n);
});

test('toDecimal converts octal 777 to 511', () => {
    const symbols = BaseConverter.getDefaultSymbols(8);
    const result = BaseConverter.toDecimal('777', 8, symbols);
    assertEqual(result.value, 511n);
});

test('toDecimal converts decimal 12345 to 12345', () => {
    const symbols = BaseConverter.getDefaultSymbols(10);
    const result = BaseConverter.toDecimal('12345', 10, symbols);
    assertEqual(result.value, 12345n);
});

test('toDecimal rejects invalid characters', () => {
    const result = BaseConverter.toDecimal('102', 2, ['0', '1']);
    assertNull(result.value);
    assertNotNull(result.error);
});

test('toDecimal rejects empty string', () => {
    const result = BaseConverter.toDecimal('', 2, ['0', '1']);
    assertNull(result.value);
    assertNotNull(result.error);
});

test('toDecimal handles large numbers', () => {
    const symbols = BaseConverter.getDefaultSymbols(16);
    const result = BaseConverter.toDecimal('FFFFFFFFFFFFFFFF', 16, symbols);
    assertEqual(result.value, 18446744073709551615n);
});

// Test: fromDecimal
console.log('\n--- fromDecimal ---');

test('fromDecimal converts 10 to binary 1010', () => {
    const result = BaseConverter.fromDecimal(10n, 2, ['0', '1']);
    assertEqual(result.value, '1010');
});

test('fromDecimal converts 255 to binary 11111111', () => {
    const result = BaseConverter.fromDecimal(255n, 2, ['0', '1']);
    assertEqual(result.value, '11111111');
});

test('fromDecimal converts 255 to hex FF', () => {
    const symbols = BaseConverter.getDefaultSymbols(16);
    const result = BaseConverter.fromDecimal(255n, 16, symbols);
    assertEqual(result.value, 'FF');
});

test('fromDecimal converts 0 to "0"', () => {
    const result = BaseConverter.fromDecimal(0n, 2, ['0', '1']);
    assertEqual(result.value, '0');
});

test('fromDecimal converts 511 to octal 777', () => {
    const symbols = BaseConverter.getDefaultSymbols(8);
    const result = BaseConverter.fromDecimal(511n, 8, symbols);
    assertEqual(result.value, '777');
});

test('fromDecimal accepts regular numbers', () => {
    const result = BaseConverter.fromDecimal(10, 2, ['0', '1']);
    assertEqual(result.value, '1010');
});

test('fromDecimal handles large numbers', () => {
    const symbols = BaseConverter.getDefaultSymbols(16);
    const result = BaseConverter.fromDecimal(18446744073709551615n, 16, symbols);
    assertEqual(result.value, 'FFFFFFFFFFFFFFFF');
});

// Test: convert
console.log('\n--- convert ---');

test('convert binary to decimal', () => {
    const result = BaseConverter.convert('1010', 2, 10);
    assertEqual(result.value, '10');
});

test('convert decimal to binary', () => {
    const result = BaseConverter.convert('10', 10, 2);
    assertEqual(result.value, '1010');
});

test('convert hex to decimal', () => {
    const result = BaseConverter.convert('FF', 16, 10);
    assertEqual(result.value, '255');
});

test('convert decimal to hex', () => {
    const result = BaseConverter.convert('255', 10, 16);
    assertEqual(result.value, 'FF');
});

test('convert binary to hex', () => {
    const result = BaseConverter.convert('11111111', 2, 16);
    assertEqual(result.value, 'FF');
});

test('convert with custom symbols', () => {
    const customSymbols = ['X', 'Y', 'Z'];
    const result = BaseConverter.convert('YXX', 3, 10, customSymbols);
    assertEqual(result.value, '9'); // 1*3^2 + 0*3 + 0 = 9
});

test('convert to custom symbols', () => {
    const customSymbols = ['X', 'Y', 'Z'];
    const result = BaseConverter.convert('9', 10, 3, null, customSymbols);
    assertEqual(result.value, 'YXX');
});

// Test: filterToValidSymbols
console.log('\n--- filterToValidSymbols ---');

test('filterToValidSymbols removes invalid chars from binary', () => {
    const result = BaseConverter.filterToValidSymbols('10102abc', 2);
    assertEqual(result, '1010');
});

test('filterToValidSymbols handles hex input', () => {
    const result = BaseConverter.filterToValidSymbols('FFggZZ', 16);
    assertEqual(result, 'FF');
});

test('filterToValidSymbols preserves valid chars', () => {
    const result = BaseConverter.filterToValidSymbols('1010', 2);
    assertEqual(result, '1010');
});

test('filterToValidSymbols normalizes case', () => {
    const result = BaseConverter.filterToValidSymbols('ff', 16);
    assertEqual(result, 'FF');
});

// Test: isValidForBase
console.log('\n--- isValidForBase ---');

test('isValidForBase returns true for valid binary', () => {
    assertEqual(BaseConverter.isValidForBase('1010', 2), true);
});

test('isValidForBase returns false for invalid binary', () => {
    assertEqual(BaseConverter.isValidForBase('1012', 2), false);
});

test('isValidForBase returns true for valid hex', () => {
    assertEqual(BaseConverter.isValidForBase('DEADBEEF', 16), true);
});

test('isValidForBase handles lowercase', () => {
    assertEqual(BaseConverter.isValidForBase('deadbeef', 16), true);
});

test('isValidForBase returns false for invalid hex', () => {
    assertEqual(BaseConverter.isValidForBase('GHIJ', 16), false);
});

// Test: parseSymbolsString
console.log('\n--- parseSymbolsString ---');

test('parseSymbolsString parses comma-separated values', () => {
    const result = BaseConverter.parseSymbolsString('0,1,2,3');
    assertEqual(result, ['0', '1', '2', '3']);
});

test('parseSymbolsString trims whitespace', () => {
    const result = BaseConverter.parseSymbolsString(' 0 , 1 , 2 ');
    assertEqual(result, ['0', '1', '2']);
});

test('parseSymbolsString handles empty string', () => {
    const result = BaseConverter.parseSymbolsString('');
    assertEqual(result, []);
});

test('parseSymbolsString filters empty entries', () => {
    const result = BaseConverter.parseSymbolsString('0,,1,');
    assertEqual(result, ['0', '1']);
});

// Summary
console.log('\n=== Summary ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log(`Total: ${passed + failed}`);

process.exit(failed > 0 ? 1 : 0);
