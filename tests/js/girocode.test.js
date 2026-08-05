/**
 * Tests for GiroCode / EPC QR Code Library
 * Run with: node tests/js/girocode.test.js
 */

const GiroCode = require('../../app/static/js/girocode.js');

let passed = 0;
let failed = 0;

function test(name, fn) {
    try {
        fn();
        console.log(`\u2713 ${name}`);
        passed++;
    } catch (e) {
        console.log(`\u2717 ${name}`);
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

console.log('=== GiroCode Tests ===\n');

// --- formatAmount ---
console.log('--- formatAmount ---');

test('formatAmount formats integer euros with 2 decimals', () => {
    assertEqual(GiroCode.formatAmount('250').value, 'EUR250.00');
});

test('formatAmount keeps 2 decimals', () => {
    assertEqual(GiroCode.formatAmount('12.3').value, 'EUR12.30');
});

test('formatAmount accepts German decimal comma', () => {
    assertEqual(GiroCode.formatAmount('12,34').value, 'EUR12.34');
});

test('formatAmount accepts German thousands + comma', () => {
    assertEqual(GiroCode.formatAmount('1.234,56').value, 'EUR1234.56');
});

test('formatAmount returns null for empty input (optional)', () => {
    assertEqual(GiroCode.formatAmount('').value, null);
    assertEqual(GiroCode.formatAmount('').error, null);
    assertEqual(GiroCode.formatAmount(null).value, null);
});

test('formatAmount rejects amount below minimum', () => {
    const r = GiroCode.formatAmount('0');
    assertEqual(r.value, null);
    assertTrue(r.error !== null);
});

test('formatAmount rejects amount above maximum', () => {
    const r = GiroCode.formatAmount('1000000000');
    assertEqual(r.value, null);
    assertTrue(r.error !== null);
});

test('formatAmount rejects non-numeric input', () => {
    const r = GiroCode.formatAmount('abc');
    assertEqual(r.value, null);
    assertTrue(r.error !== null);
});

// --- isValidBic ---
console.log('\n--- isValidBic ---');

test('isValidBic accepts 8-char BIC', () => {
    assertTrue(GiroCode.isValidBic('COBADEFF'));
});

test('isValidBic accepts 11-char BIC', () => {
    assertTrue(GiroCode.isValidBic('COBADEFFXXX'));
});

test('isValidBic rejects wrong length', () => {
    assertFalse(GiroCode.isValidBic('COBADEF'));
    assertFalse(GiroCode.isValidBic('COBADEFFXX'));
});

// --- build ---
console.log('\n--- build ---');

test('build produces a valid EPC payload with all fields', () => {
    const r = GiroCode.build({
        name: 'Red Cross',
        iban: 'DE89370400440532013000',
        bic: 'COBADEFFXXX',
        amount: '250.00',
        reference: 'Invoice INV-2025-001'
    });
    assertTrue(r.valid, r.errors.join(', '));
    const expected = [
        'BCD', '002', '1', 'SCT',
        'COBADEFFXXX', 'Red Cross', 'DE89370400440532013000',
        'EUR250.00', '', '', 'Invoice INV-2025-001'
    ].join('\n');
    assertEqual(r.payload, expected);
});

test('build works without BIC (version 002)', () => {
    const r = GiroCode.build({
        name: 'Max Mustermann',
        iban: 'DE89370400440532013000',
        amount: '12,34',
        reference: 'Danke'
    });
    assertTrue(r.valid, r.errors.join(', '));
    const lines = r.payload.split('\n');
    assertEqual(lines[4], ''); // empty BIC line
    assertEqual(lines[7], 'EUR12.34');
    assertEqual(lines[10], 'Danke');
    assertEqual(lines.length, 11);
});

test('build works without amount (payment request open amount)', () => {
    const r = GiroCode.build({
        name: 'Max Mustermann',
        iban: 'DE89370400440532013000'
    });
    assertTrue(r.valid, r.errors.join(', '));
    const lines = r.payload.split('\n');
    assertEqual(lines[7], ''); // empty amount line
});

test('build rejects missing name', () => {
    const r = GiroCode.build({ iban: 'DE89370400440532013000' });
    assertFalse(r.valid);
    assertEqual(r.payload, null);
});

test('build rejects missing IBAN', () => {
    const r = GiroCode.build({ name: 'Test' });
    assertFalse(r.valid);
});

test('build rejects invalid IBAN checksum', () => {
    const r = GiroCode.build({ name: 'Test', iban: 'DE00370400440532013000' });
    assertFalse(r.valid);
});

test('build rejects invalid BIC', () => {
    const r = GiroCode.build({ name: 'Test', iban: 'DE89370400440532013000', bic: 'BADBIC' });
    assertFalse(r.valid);
});

test('build rejects name over 70 chars', () => {
    const r = GiroCode.build({ name: 'x'.repeat(71), iban: 'DE89370400440532013000' });
    assertFalse(r.valid);
});

test('build rejects reference over 140 chars', () => {
    const r = GiroCode.build({
        name: 'Test',
        iban: 'DE89370400440532013000',
        reference: 'x'.repeat(141)
    });
    assertFalse(r.valid);
});

test('byteLength counts multibyte UTF-8 characters', () => {
    assertEqual(GiroCode.byteLength('abc'), 3);
    assertEqual(GiroCode.byteLength('\u00e4\u00f6\u00fc'), 6); // äöü -> 2 bytes each
});

test('build stays within payload byte limit at max field lengths', () => {
    const r = GiroCode.build({
        name: 'x'.repeat(70),
        iban: 'DE89370400440532013000',
        bic: 'COBADEFFXXX',
        purpose: 'CHAR',
        reference: 'y'.repeat(140)
    });
    assertTrue(r.valid, r.errors.join(', '));
    assertTrue(GiroCode.byteLength(r.payload) <= GiroCode.MAX_PAYLOAD_BYTES);
});

test('build normalizes IBAN spacing and case', () => {
    const r = GiroCode.build({
        name: 'Test',
        iban: 'de89 3704 0044 0532 0130 00'
    });
    assertTrue(r.valid, r.errors.join(', '));
    assertEqual(r.payload.split('\n')[6], 'DE89370400440532013000');
});

console.log(`\n=== Results: ${passed} passed, ${failed} failed ===`);
process.exit(failed === 0 ? 0 : 1);
