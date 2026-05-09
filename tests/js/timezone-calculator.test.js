/**
 * Tests for Timezone Calculator
 */

const TimezoneCalculator = require('../../app/static/js/timezone-calculator.js');

// Test utilities
let passed = 0;
let failed = 0;

function assert(condition, message) {
    if (condition) {
        console.log(`✓ ${message}`);
        passed++;
    } else {
        console.error(`✗ ${message}`);
        failed++;
    }
}

function assertThrows(fn, message) {
    try {
        fn();
        console.error(`✗ ${message} (did not throw)`);
        failed++;
    } catch (e) {
        console.log(`✓ ${message}`);
        passed++;
    }
}

console.log('=== Timezone Calculator Tests ===\n');

// --- getTimezones ---
console.log('--- getTimezones ---');
const timezones = TimezoneCalculator.getTimezones();
assert(Array.isArray(timezones), 'getTimezones returns array');
assert(timezones.length > 0, 'getTimezones returns non-empty array');
assert(timezones.length > 400, 'getTimezones returns many timezones (>400)');
assert(timezones.includes('America/New_York'), 'getTimezones includes America/New_York');
assert(timezones.includes('Europe/Berlin'), 'getTimezones includes Europe/Berlin');

// --- getLocalTimezone ---
console.log('\n--- getLocalTimezone ---');
const localTz = TimezoneCalculator.getLocalTimezone();
assert(typeof localTz === 'string', 'getLocalTimezone returns string');
assert(localTz.length > 0, 'getLocalTimezone returns non-empty string');

// --- isValidTimezone ---
console.log('\n--- isValidTimezone ---');
assert(TimezoneCalculator.isValidTimezone('UTC'), 'isValidTimezone: UTC is valid');
assert(TimezoneCalculator.isValidTimezone('America/New_York'), 'isValidTimezone: America/New_York is valid');
assert(TimezoneCalculator.isValidTimezone('Europe/Berlin'), 'isValidTimezone: Europe/Berlin is valid');
assert(!TimezoneCalculator.isValidTimezone('Invalid/Timezone'), 'isValidTimezone: Invalid/Timezone is invalid');
assert(!TimezoneCalculator.isValidTimezone(''), 'isValidTimezone: empty string is invalid');

// --- parseTimeInput ---
console.log('\n--- parseTimeInput ---');

// ISO format
const isoDate = TimezoneCalculator.parseTimeInput('2026-05-09T14:30:00');
assert(isoDate instanceof Date, 'parseTimeInput: ISO format returns Date');
assert(isoDate.getFullYear() === 2026, 'parseTimeInput: ISO year is 2026');
assert(isoDate.getMonth() === 4, 'parseTimeInput: ISO month is May (4)');
assert(isoDate.getDate() === 9, 'parseTimeInput: ISO day is 9');

// Unix timestamp (seconds)
const unixDate = TimezoneCalculator.parseTimeInput('1715265000');
assert(unixDate instanceof Date, 'parseTimeInput: Unix timestamp returns Date');

// Unix timestamp (milliseconds)
const unixMillisDate = TimezoneCalculator.parseTimeInput('1715265000000');
assert(unixMillisDate instanceof Date, 'parseTimeInput: Unix milliseconds returns Date');

// Time only (24-hour)
const time24 = TimezoneCalculator.parseTimeInput('14:30');
assert(time24 instanceof Date, 'parseTimeInput: 24-hour time returns Date');
assert(time24.getHours() === 14, 'parseTimeInput: 24-hour hours is 14');
assert(time24.getMinutes() === 30, 'parseTimeInput: 24-hour minutes is 30');

// Time only (12-hour PM)
const time12pm = TimezoneCalculator.parseTimeInput('2:30 PM');
assert(time12pm instanceof Date, 'parseTimeInput: 12-hour PM returns Date');
assert(time12pm.getHours() === 14, 'parseTimeInput: 2:30 PM is 14:30');

// Time only (12-hour AM)
const time12am = TimezoneCalculator.parseTimeInput('2:30 AM');
assert(time12am instanceof Date, 'parseTimeInput: 12-hour AM returns Date');
assert(time12am.getHours() === 2, 'parseTimeInput: 2:30 AM is 02:30');

// Noon edge case
const noon = TimezoneCalculator.parseTimeInput('12:00 PM');
assert(noon.getHours() === 12, 'parseTimeInput: 12:00 PM is 12:00');

// Midnight edge case
const midnight = TimezoneCalculator.parseTimeInput('12:00 AM');
assert(midnight.getHours() === 0, 'parseTimeInput: 12:00 AM is 00:00');

// Invalid inputs
assert(TimezoneCalculator.parseTimeInput('invalid') === null, 'parseTimeInput: invalid string returns null');
assert(TimezoneCalculator.parseTimeInput('') === null, 'parseTimeInput: empty string returns null');
assert(TimezoneCalculator.parseTimeInput(null) === null, 'parseTimeInput: null returns null');

// --- formatInTimezone ---
console.log('\n--- formatInTimezone ---');
const testDate = new Date('2026-05-09T12:00:00Z');
const utcFormatted = TimezoneCalculator.formatInTimezone(testDate, 'UTC');
assert(typeof utcFormatted === 'string', 'formatInTimezone returns string');
assert(utcFormatted.includes('2026'), 'formatInTimezone includes year');
assert(utcFormatted.includes('05'), 'formatInTimezone includes month');
assert(utcFormatted.includes('09'), 'formatInTimezone includes day');

// --- getTimezoneOffset ---
console.log('\n--- getTimezoneOffset ---');
const summerDate = new Date('2026-07-01T12:00:00Z'); // Summer (DST active in many zones)
const winterDate = new Date('2026-01-01T12:00:00Z'); // Winter (DST inactive)

const utcOffset = TimezoneCalculator.getTimezoneOffset(testDate, 'UTC');
assert(utcOffset === '+00:00', 'getTimezoneOffset: UTC is +00:00');

// Test DST handling (New York has DST)
const nyWinterOffset = TimezoneCalculator.getTimezoneOffset(winterDate, 'America/New_York');
const nySummerOffset = TimezoneCalculator.getTimezoneOffset(summerDate, 'America/New_York');
assert(nyWinterOffset === '-05:00', 'getTimezoneOffset: NY winter is -05:00 (EST)');
assert(nySummerOffset === '-04:00', 'getTimezoneOffset: NY summer is -04:00 (EDT)');

// --- convert ---
console.log('\n--- convert ---');
const conversionDate = new Date('2026-05-09T14:00:00Z');
const result = TimezoneCalculator.convert(conversionDate, 'UTC', 'America/New_York');

assert(typeof result === 'object', 'convert returns object');
assert(result.source.timezone === 'UTC', 'convert: source timezone is UTC');
assert(result.target.timezone === 'America/New_York', 'convert: target timezone is America/New_York');
assert(typeof result.source.formatted === 'string', 'convert: source formatted is string');
assert(typeof result.target.formatted === 'string', 'convert: target formatted is string');
assert(result.source.offset === '+00:00', 'convert: source offset is +00:00');
assert(result.target.offset === '-04:00', 'convert: target offset is -04:00 (May = EDT)');
assert(result.date === conversionDate, 'convert: date is preserved');

// Test error handling
assertThrows(() => TimezoneCalculator.convert(null, 'UTC', 'America/New_York'), 'convert throws on null date');
assertThrows(() => TimezoneCalculator.convert(new Date('invalid'), 'UTC', 'America/New_York'), 'convert throws on invalid date');
assertThrows(() => TimezoneCalculator.convert(testDate, '', 'America/New_York'), 'convert throws on empty source timezone');
assertThrows(() => TimezoneCalculator.convert(testDate, 'UTC', ''), 'convert throws on empty target timezone');

// --- DST Transition Tests ---
console.log('\n--- DST Transition Tests ---');

// Test a specific DST transition (US Spring Forward 2026: March 8, 2:00 AM -> 3:00 AM)
const beforeDST = new Date('2026-03-07T12:00:00Z');
const afterDST = new Date('2026-03-09T12:00:00Z');

const beforeOffset = TimezoneCalculator.getTimezoneOffset(beforeDST, 'America/New_York');
const afterOffset = TimezoneCalculator.getTimezoneOffset(afterDST, 'America/New_York');

assert(beforeOffset === '-05:00', 'DST: Before spring forward is EST (-05:00)');
assert(afterOffset === '-04:00', 'DST: After spring forward is EDT (-04:00)');

// Test Europe/Berlin DST (different dates than US)
const berlinWinter = new Date('2026-01-15T12:00:00Z');
const berlinSummer = new Date('2026-07-15T12:00:00Z');

const berlinWinterOffset = TimezoneCalculator.getTimezoneOffset(berlinWinter, 'Europe/Berlin');
const berlinSummerOffset = TimezoneCalculator.getTimezoneOffset(berlinSummer, 'Europe/Berlin');

assert(berlinWinterOffset === '+01:00', 'DST: Berlin winter is CET (+01:00)');
assert(berlinSummerOffset === '+02:00', 'DST: Berlin summer is CEST (+02:00)');

// --- Summary ---
console.log('\n=== Summary ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log(`Total: ${passed + failed}`);

process.exit(failed > 0 ? 1 : 0);
