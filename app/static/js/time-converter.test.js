/**
 * Tests for TimeConverter library
 * Run with: node time-converter.test.js
 */

const TimeConverter = require('./time-converter.js');

let passed = 0;
let failed = 0;

function test(name, fn) {
    try {
        fn();
        console.log('✓ ' + name);
        passed++;
    } catch (e) {
        console.log('✗ ' + name);
        console.log('  Error: ' + e.message);
        failed++;
    }
}

function assertEqual(actual, expected, message) {
    if (actual !== expected) {
        throw new Error((message || '') + ' Expected: ' + expected + ', Got: ' + actual);
    }
}

function assertTrue(value, message) {
    if (!value) {
        throw new Error(message || 'Expected true but got false');
    }
}

function assertFalse(value, message) {
    if (value) {
        throw new Error(message || 'Expected false but got true');
    }
}

function assertNotNull(value, message) {
    if (value === null || value === undefined) {
        throw new Error(message || 'Expected non-null value');
    }
}

function assertNull(value, message) {
    if (value !== null) {
        throw new Error(message || 'Expected null but got: ' + value);
    }
}

console.log('\n=== TimeConverter Tests ===\n');

// Parse tests
console.log('--- Parsing ---');

test('parse Unix timestamp (seconds)', function() {
    const date = TimeConverter.parse('1737284400');
    assertNotNull(date);
    assertEqual(date.getTime(), 1737284400000);
});

test('parse Unix timestamp (milliseconds)', function() {
    const date = TimeConverter.parse('1737284400000');
    assertNotNull(date);
    assertEqual(date.getTime(), 1737284400000);
});

test('parse ISO 8601', function() {
    const date = TimeConverter.parse('2026-01-19T11:00:00.000Z');
    assertNotNull(date);
    assertEqual(date.toISOString(), '2026-01-19T11:00:00.000Z');
});

test('parse RFC 2822', function() {
    const date = TimeConverter.parse('Mon, 19 Jan 2026 11:00:00 +0000');
    assertNotNull(date);
    assertEqual(date.getUTCFullYear(), 2026);
    assertEqual(date.getUTCMonth(), 0); // January
    assertEqual(date.getUTCDate(), 19);
});

test('parse US format MM/DD/YYYY', function() {
    const date = TimeConverter.parse('01/19/2026');
    assertNotNull(date);
    assertEqual(date.getFullYear(), 2026);
    assertEqual(date.getMonth(), 0);
    assertEqual(date.getDate(), 19);
});

test('parse US format with time', function() {
    const date = TimeConverter.parse('01/19/2026 @ 11:30am');
    assertNotNull(date);
    assertEqual(date.getFullYear(), 2026);
    assertEqual(date.getHours(), 11);
    assertEqual(date.getMinutes(), 30);
});

test('parse returns null for invalid input', function() {
    assertNull(TimeConverter.parse('not a date'));
    assertNull(TimeConverter.parse(''));
    assertNull(TimeConverter.parse(null));
});

// Format validation tests
console.log('\n--- Format Validation ---');

test('validateFormatString accepts valid formats', function() {
    assertTrue(TimeConverter.validateFormatString('%Y-%m-%d'));
    assertTrue(TimeConverter.validateFormatString('%H:%M:%S'));
    assertTrue(TimeConverter.validateFormatString('%Y-%m-%dT%H:%M:%S%z'));
    assertTrue(TimeConverter.validateFormatString('%%'));
});

test('validateFormatString rejects invalid formats', function() {
    assertFalse(TimeConverter.validateFormatString('%Q')); // Not a valid directive
    assertFalse(TimeConverter.validateFormatString('%!')); // Invalid
    assertFalse(TimeConverter.validateFormatString(null));
    assertFalse(TimeConverter.validateFormatString(''));
});

test('validateFormatString rejects overly long formats', function() {
    const longFormat = '%Y'.repeat(60); // 120 chars
    assertFalse(TimeConverter.validateFormatString(longFormat));
});

// strftime tests
console.log('\n--- strftime ---');

test('strftime %Y returns full year', function() {
    const date = new Date(2026, 0, 19, 11, 30, 45);
    assertEqual(TimeConverter.strftime(date, '%Y'), '2026');
});

test('strftime %m returns zero-padded month', function() {
    const date = new Date(2026, 0, 19);
    assertEqual(TimeConverter.strftime(date, '%m'), '01');
});

test('strftime %d returns zero-padded day', function() {
    const date = new Date(2026, 0, 9);
    assertEqual(TimeConverter.strftime(date, '%d'), '09');
});

test('strftime %H returns 24-hour format', function() {
    const date = new Date(2026, 0, 19, 15, 30, 0);
    assertEqual(TimeConverter.strftime(date, '%H'), '15');
});

test('strftime %I returns 12-hour format', function() {
    const date = new Date(2026, 0, 19, 15, 30, 0);
    assertEqual(TimeConverter.strftime(date, '%I'), '03');
});

test('strftime %p returns AM/PM', function() {
    const am = new Date(2026, 0, 19, 9, 0, 0);
    const pm = new Date(2026, 0, 19, 15, 0, 0);
    assertEqual(TimeConverter.strftime(am, '%p'), 'AM');
    assertEqual(TimeConverter.strftime(pm, '%p'), 'PM');
});

test('strftime %A returns full weekday name', function() {
    const monday = new Date(2026, 0, 19); // Jan 19, 2026 is a Monday
    assertEqual(TimeConverter.strftime(monday, '%A'), 'Monday');
});

test('strftime %B returns full month name', function() {
    const date = new Date(2026, 0, 19);
    assertEqual(TimeConverter.strftime(date, '%B'), 'January');
});

test('strftime %F returns ISO date format', function() {
    const date = new Date(2026, 0, 19);
    assertEqual(TimeConverter.strftime(date, '%F'), '2026-01-19');
});

test('strftime %T returns time format', function() {
    const date = new Date(2026, 0, 19, 11, 30, 45);
    assertEqual(TimeConverter.strftime(date, '%T'), '11:30:45');
});

test('strftime combined format', function() {
    const date = new Date(2026, 0, 19, 11, 30, 45);
    assertEqual(TimeConverter.strftime(date, '%Y-%m-%d %H:%M:%S'), '2026-01-19 11:30:45');
});

test('strftime returns null for invalid format', function() {
    const date = new Date(2026, 0, 19);
    assertNull(TimeConverter.strftime(date, '%Q'));
});

test('strftime returns null for invalid date', function() {
    assertNull(TimeConverter.strftime(new Date('invalid'), '%Y'));
    assertNull(TimeConverter.strftime(null, '%Y'));
});

// Format method tests
console.log('\n--- format() ---');

test('format unix_seconds', function() {
    const date = new Date(1737284400000);
    assertEqual(TimeConverter.format(date, 'unix_seconds'), '1737284400');
});

test('format unix_millis', function() {
    const date = new Date(1737284400000);
    assertEqual(TimeConverter.format(date, 'unix_millis'), '1737284400000');
});

test('format iso8601', function() {
    const date = new Date('2026-01-19T11:00:00.000Z');
    assertEqual(TimeConverter.format(date, 'iso8601'), '2026-01-19T11:00:00.000Z');
});

test('format rfc3339', function() {
    const date = new Date('2026-01-19T11:00:00.000Z');
    assertEqual(TimeConverter.format(date, 'rfc3339'), '2026-01-19T11:00:00.000Z');
});

// Utility function tests
console.log('\n--- Utility Functions ---');

test('toUnixSeconds', function() {
    const date = new Date(1737284400000);
    assertEqual(TimeConverter.toUnixSeconds(date), 1737284400);
});

test('toUnixMillis', function() {
    const date = new Date(1737284400000);
    assertEqual(TimeConverter.toUnixMillis(date), 1737284400000);
});

test('getDayOfYear', function() {
    const jan1 = new Date(2026, 0, 1);
    const jan19 = new Date(2026, 0, 19);
    assertEqual(TimeConverter.getDayOfYear(jan1), 1);
    assertEqual(TimeConverter.getDayOfYear(jan19), 19);
});

test('getISOWeekNumber', function() {
    const date = new Date(2026, 0, 19); // Week 4 of 2026
    assertTrue(TimeConverter.getISOWeekNumber(date) >= 1);
    assertTrue(TimeConverter.getISOWeekNumber(date) <= 53);
});

test('getTimezoneOffset returns valid format', function() {
    const date = new Date();
    const offset = TimeConverter.getTimezoneOffset(date);
    assertTrue(/^[+-]\d{4}$/.test(offset), 'Should match +/-HHMM format');
});

// getAllFormats test
console.log('\n--- getAllFormats ---');

test('getAllFormats returns all formats', function() {
    const date = new Date('2026-01-19T11:00:00.000Z');
    const formats = TimeConverter.getAllFormats(date);
    assertNotNull(formats);
    assertNotNull(formats.unix_seconds);
    assertNotNull(formats.unix_millis);
    assertNotNull(formats.iso8601);
    assertNotNull(formats.rfc3339);
    assertNotNull(formats.rfc2822);
    assertNotNull(formats.utc);
    assertNotNull(formats.local);
    assertNotNull(formats.date_only);
    assertNotNull(formats.time_only);
});

test('getAllFormats returns null for invalid date', function() {
    assertNull(TimeConverter.getAllFormats(new Date('invalid')));
});

// Summary
console.log('\n=== Results ===');
console.log('Passed: ' + passed);
console.log('Failed: ' + failed);
console.log('');

if (failed > 0) {
    process.exit(1);
}
