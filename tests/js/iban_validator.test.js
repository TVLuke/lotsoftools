/**
 * Tests for IBAN Validator Library
 * Run with: node tests/js/iban_validator.test.js
 */

const IbanValidator = require('../../app/static/js/iban_validator.js');

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
    const actualStr = JSON.stringify(actual);
    const expectedStr = JSON.stringify(expected);
    if (actualStr !== expectedStr) {
        throw new Error(`${msg}\n  Expected: ${expectedStr}\n  Actual: ${actualStr}`);
    }
}

function assertTrue(actual, msg = '') {
    if (actual !== true) {
        throw new Error(`${msg}\n  Expected true, got: ${actual}`);
    }
}

function assertFalse(actual, msg = '') {
    if (actual !== false) {
        throw new Error(`${msg}\n  Expected false, got: ${actual}`);
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

console.log('=== IBAN Validator Tests ===\n');

// Test: cleanIban
console.log('--- cleanIban ---');

test('cleanIban removes spaces', () => {
    assertEqual(IbanValidator.cleanIban('DE89 3704 0044 0532 0130 00'), 'DE89370400440532013000');
});

test('cleanIban converts to uppercase', () => {
    assertEqual(IbanValidator.cleanIban('de89370400440532013000'), 'DE89370400440532013000');
});

test('cleanIban handles empty input', () => {
    assertEqual(IbanValidator.cleanIban(''), '');
    assertEqual(IbanValidator.cleanIban(null), '');
    assertEqual(IbanValidator.cleanIban(undefined), '');
});

// Test: formatIban
console.log('\n--- formatIban ---');

test('formatIban adds spaces every 4 characters', () => {
    assertEqual(IbanValidator.formatIban('DE89370400440532013000'), 'DE89 3704 0044 0532 0130 00');
});

test('formatIban handles already spaced input', () => {
    assertEqual(IbanValidator.formatIban('DE89 3704 0044'), 'DE89 3704 0044');
});

test('formatIban handles short input', () => {
    assertEqual(IbanValidator.formatIban('DE89'), 'DE89');
});

// Test: getCountryCode
console.log('\n--- getCountryCode ---');

test('getCountryCode extracts country code', () => {
    assertEqual(IbanValidator.getCountryCode('DE89370400440532013000'), 'DE');
    assertEqual(IbanValidator.getCountryCode('GB82WEST12345698765432'), 'GB');
    assertEqual(IbanValidator.getCountryCode('FR7630006000011234567890189'), 'FR');
});

// Test: getCheckDigits
console.log('\n--- getCheckDigits ---');

test('getCheckDigits extracts check digits', () => {
    assertEqual(IbanValidator.getCheckDigits('DE89370400440532013000'), '89');
    assertEqual(IbanValidator.getCheckDigits('GB82WEST12345698765432'), '82');
});

// Test: getBban
console.log('\n--- getBban ---');

test('getBban extracts BBAN', () => {
    assertEqual(IbanValidator.getBban('DE89370400440532013000'), '370400440532013000');
    assertEqual(IbanValidator.getBban('GB82WEST12345698765432'), 'WEST12345698765432');
});

// Test: getCountryName
console.log('\n--- getCountryName ---');

test('getCountryName returns country name', () => {
    assertEqual(IbanValidator.getCountryName('DE'), 'Germany');
    assertEqual(IbanValidator.getCountryName('GB'), 'United Kingdom');
    assertEqual(IbanValidator.getCountryName('FR'), 'France');
    assertEqual(IbanValidator.getCountryName('NL'), 'Netherlands');
});

test('getCountryName handles lowercase', () => {
    assertEqual(IbanValidator.getCountryName('de'), 'Germany');
});

test('getCountryName returns null for unknown', () => {
    assertNull(IbanValidator.getCountryName('XX'));
});

// Test: getExpectedLength
console.log('\n--- getExpectedLength ---');

test('getExpectedLength returns correct lengths', () => {
    assertEqual(IbanValidator.getExpectedLength('DE'), 22);
    assertEqual(IbanValidator.getExpectedLength('GB'), 22);
    assertEqual(IbanValidator.getExpectedLength('FR'), 27);
    assertEqual(IbanValidator.getExpectedLength('NL'), 18);
    assertEqual(IbanValidator.getExpectedLength('BE'), 16);
    assertEqual(IbanValidator.getExpectedLength('AT'), 20);
});

test('getExpectedLength returns null for unknown', () => {
    assertNull(IbanValidator.getExpectedLength('XX'));
});

// Test: isValidCountryCode
console.log('\n--- isValidCountryCode ---');

test('isValidCountryCode returns true for valid codes', () => {
    assertTrue(IbanValidator.isValidCountryCode('DE'));
    assertTrue(IbanValidator.isValidCountryCode('GB'));
    assertTrue(IbanValidator.isValidCountryCode('FR'));
});

test('isValidCountryCode returns false for invalid codes', () => {
    assertFalse(IbanValidator.isValidCountryCode('XX'));
    assertFalse(IbanValidator.isValidCountryCode('ZZ'));
});

// Test: validateFormat
console.log('\n--- validateFormat ---');

test('validateFormat accepts valid format', () => {
    const result = IbanValidator.validateFormat('DE89370400440532013000');
    assertTrue(result.valid);
    assertNull(result.error);
});

test('validateFormat rejects empty input', () => {
    const result = IbanValidator.validateFormat('');
    assertFalse(result.valid);
    assertNotNull(result.error);
});

test('validateFormat rejects too short input', () => {
    const result = IbanValidator.validateFormat('DE89');
    assertFalse(result.valid);
});

test('validateFormat rejects invalid country code', () => {
    const result = IbanValidator.validateFormat('12893704004405320130');
    assertFalse(result.valid);
});

test('validateFormat rejects invalid check digits', () => {
    const result = IbanValidator.validateFormat('DEAB370400440532013000');
    assertFalse(result.valid);
});

// Test: validateLength
console.log('\n--- validateLength ---');

test('validateLength accepts correct length', () => {
    const result = IbanValidator.validateLength('DE89370400440532013000');
    assertTrue(result.valid);
});

test('validateLength rejects incorrect length', () => {
    const result = IbanValidator.validateLength('DE8937040044053201300'); // 21 chars, should be 22
    assertFalse(result.valid);
});

test('validateLength rejects unknown country', () => {
    const result = IbanValidator.validateLength('XX89370400440532013000');
    assertFalse(result.valid);
});

// Test: validateChecksum
console.log('\n--- validateChecksum ---');

test('validateChecksum returns true for valid IBANs', () => {
    // These are well-known test IBANs
    assertTrue(IbanValidator.validateChecksum('DE89370400440532013000'));
    assertTrue(IbanValidator.validateChecksum('GB82WEST12345698765432'));
    assertTrue(IbanValidator.validateChecksum('FR7630006000011234567890189'));
    assertTrue(IbanValidator.validateChecksum('NL91ABNA0417164300'));
});

test('validateChecksum returns false for invalid checksums', () => {
    // Same IBANs with wrong check digits
    assertFalse(IbanValidator.validateChecksum('DE00370400440532013000'));
    assertFalse(IbanValidator.validateChecksum('GB00WEST12345698765432'));
});

// Test: validate (full validation)
console.log('\n--- validate ---');

test('validate returns valid for correct German IBAN', () => {
    const result = IbanValidator.validate('DE89370400440532013000');
    assertTrue(result.valid);
    assertEqual(result.errors.length, 0);
    assertEqual(result.countryCode, 'DE');
    assertEqual(result.countryName, 'Germany');
    assertEqual(result.checkDigits, '89');
    assertEqual(result.bban, '370400440532013000');
});

test('validate returns valid for correct UK IBAN', () => {
    const result = IbanValidator.validate('GB82WEST12345698765432');
    assertTrue(result.valid);
    assertEqual(result.countryCode, 'GB');
    assertEqual(result.countryName, 'United Kingdom');
});

test('validate returns valid for correct French IBAN', () => {
    const result = IbanValidator.validate('FR7630006000011234567890189');
    assertTrue(result.valid);
    assertEqual(result.countryCode, 'FR');
});

test('validate returns valid for correct Dutch IBAN', () => {
    const result = IbanValidator.validate('NL91ABNA0417164300');
    assertTrue(result.valid);
    assertEqual(result.countryCode, 'NL');
});

test('validate handles spaces in input', () => {
    const result = IbanValidator.validate('DE89 3704 0044 0532 0130 00');
    assertTrue(result.valid);
});

test('validate handles lowercase input', () => {
    const result = IbanValidator.validate('de89370400440532013000');
    assertTrue(result.valid);
});

test('validate returns invalid for wrong checksum', () => {
    const result = IbanValidator.validate('DE00370400440532013000');
    assertFalse(result.valid);
    assertTrue(result.errors.length > 0);
});

test('validate returns invalid for wrong length', () => {
    const result = IbanValidator.validate('DE893704004405320130'); // Too short
    assertFalse(result.valid);
});

test('validate returns invalid for unknown country', () => {
    const result = IbanValidator.validate('XX89370400440532013000');
    assertFalse(result.valid);
});

test('validate returns formatted IBAN', () => {
    const result = IbanValidator.validate('DE89370400440532013000');
    assertEqual(result.formatted, 'DE89 3704 0044 0532 0130 00');
});

// Test: generateCheckDigits
console.log('\n--- generateCheckDigits ---');

test('generateCheckDigits generates correct digits for DE', () => {
    const result = IbanValidator.generateCheckDigits('DE', '370400440532013000');
    assertEqual(result.checkDigits, '89');
    assertNull(result.error);
});

test('generateCheckDigits generates correct digits for GB', () => {
    const result = IbanValidator.generateCheckDigits('GB', 'WEST12345698765432');
    assertEqual(result.checkDigits, '82');
});

test('generateCheckDigits generates correct digits for NL', () => {
    const result = IbanValidator.generateCheckDigits('NL', 'ABNA0417164300');
    assertEqual(result.checkDigits, '91');
});

test('generateCheckDigits returns error for unknown country', () => {
    const result = IbanValidator.generateCheckDigits('XX', '123456789');
    assertNull(result.checkDigits);
    assertNotNull(result.error);
});

// Summary
console.log('\n=== Summary ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log(`Total: ${passed + failed}`);

process.exit(failed > 0 ? 1 : 0);
