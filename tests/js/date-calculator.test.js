const DateCalculator = require('../../app/static/js/date-calculator.js');

let passed = 0;
let failed = 0;

function assert(condition, message) {
    if (condition) {
        console.log(`✓ ${message}`);
        passed++;
    } else {
        console.log(`✗ ${message}`);
        failed++;
    }
}

console.log('=== Date Calculator Tests ===\n');

// Test formatNumber
console.log('--- formatNumber ---');
assert(DateCalculator.formatNumber(1000) === '1.000', 'formatNumber: 1000 -> 1.000');
assert(DateCalculator.formatNumber(1000000) === '1.000.000', 'formatNumber: 1000000 -> 1.000.000');
assert(DateCalculator.formatNumber(123) === '123', 'formatNumber: 123 -> 123');
assert(DateCalculator.formatNumber(0) === '0', 'formatNumber: 0 -> 0');

// Test calculateDifference with known dates
console.log('\n--- calculateDifference ---');

// Test: exactly 1 day difference
const date1 = new Date('2025-01-15T12:00:00');
const date2 = new Date('2025-01-14T12:00:00');
const diff1Day = DateCalculator.calculateDifference(date1, date2);

assert(diff1Day.isNegative === false, 'calculateDifference: 1 day positive');
assert(diff1Day.totalDays === 1, 'calculateDifference: totalDays is 1');
assert(diff1Day.totalHours === 24, 'calculateDifference: totalHours is 24');
assert(diff1Day.totalMinutes === 1440, 'calculateDifference: totalMinutes is 1440');
assert(diff1Day.totalSeconds === 86400, 'calculateDifference: totalSeconds is 86400');

// Test: negative difference (date2 > date1)
const diffNegative = DateCalculator.calculateDifference(date2, date1);
assert(diffNegative.isNegative === true, 'calculateDifference: negative when date2 > date1');
assert(diffNegative.prefix === '-', 'calculateDifference: prefix is "-" when negative');

// Test: exactly 1 hour difference
const date3 = new Date('2025-01-15T13:00:00');
const date4 = new Date('2025-01-15T12:00:00');
const diff1Hour = DateCalculator.calculateDifference(date3, date4);

assert(diff1Hour.totalHours === 1, 'calculateDifference: 1 hour totalHours is 1');
assert(diff1Hour.totalMinutes === 60, 'calculateDifference: 1 hour totalMinutes is 60');
assert(diff1Hour.totalSeconds === 3600, 'calculateDifference: 1 hour totalSeconds is 3600');

// Test: exactly 1 year difference (approximate)
const date5 = new Date('2026-01-15T12:00:00');
const date6 = new Date('2025-01-15T12:00:00');
const diff1Year = DateCalculator.calculateDifference(date5, date6);

assert(diff1Year.totalDays === 365, 'calculateDifference: 1 year totalDays is 365');
assert(diff1Year.years === 0 || diff1Year.years === 1, 'calculateDifference: years is 0 or 1 (due to 365.25 calculation)');

// Test: zero difference
const sameDate = new Date('2025-01-15T12:00:00');
const diffZero = DateCalculator.calculateDifference(sameDate, sameDate);

assert(diffZero.totalSeconds === 0, 'calculateDifference: same date totalSeconds is 0');
assert(diffZero.totalDays === 0, 'calculateDifference: same date totalDays is 0');
assert(diffZero.isNegative === false, 'calculateDifference: same date not negative');

// Test format functions
console.log('\n--- Format Functions ---');

// Use a fixed difference for formatting tests
const formatDate1 = new Date('2025-02-20T15:30:45');
const formatDate2 = new Date('2025-01-15T12:00:00');
const formatDiff = DateCalculator.calculateDifference(formatDate1, formatDate2);

// Test formatFull
const fullResult = DateCalculator.formatFull(formatDiff);
assert(fullResult.includes('y'), 'formatFull: contains years');
assert(fullResult.includes('m'), 'formatFull: contains months');
assert(fullResult.includes('d'), 'formatFull: contains days');
assert(fullResult.includes(':'), 'formatFull: contains time separator');

// Test formatYearsDecimal
const yearsResult = DateCalculator.formatYearsDecimal(formatDiff);
assert(yearsResult.includes('.'), 'formatYearsDecimal: contains decimal point');

// Test formatDays
const daysResult = DateCalculator.formatDays(formatDiff);
assert(daysResult.includes('d'), 'formatDays: contains d for days');
assert(daysResult.includes(':'), 'formatDays: contains time separator');

// Test formatHours
const hoursResult = DateCalculator.formatHours(formatDiff);
assert(hoursResult.includes(':'), 'formatHours: contains time separator');
assert(hoursResult.split(':').length === 3, 'formatHours: has HH:MM:SS format');

// Test formatMinutes
const minutesResult = DateCalculator.formatMinutes(formatDiff);
assert(minutesResult.includes(':'), 'formatMinutes: contains separator');
assert(minutesResult.split(':').length === 2, 'formatMinutes: has MM:SS format');

// Test formatSeconds
const secondsResult = DateCalculator.formatSeconds(formatDiff);
assert(!secondsResult.includes(':'), 'formatSeconds: no separator');

// Test getAllFormats
console.log('\n--- getAllFormats ---');
const allFormats = DateCalculator.getAllFormats(formatDate1, formatDate2);

assert(typeof allFormats.full === 'string', 'getAllFormats: has full property');
assert(typeof allFormats.yearsDecimal === 'string', 'getAllFormats: has yearsDecimal property');
assert(typeof allFormats.days === 'string', 'getAllFormats: has days property');
assert(typeof allFormats.hours === 'string', 'getAllFormats: has hours property');
assert(typeof allFormats.minutes === 'string', 'getAllFormats: has minutes property');
assert(typeof allFormats.seconds === 'string', 'getAllFormats: has seconds property');
assert(typeof allFormats.raw === 'object', 'getAllFormats: has raw property');
assert(allFormats.raw.totalDays !== undefined, 'getAllFormats: raw has totalDays');

// Test with negative difference
console.log('\n--- Negative Difference Formatting ---');
const negFormats = DateCalculator.getAllFormats(formatDate2, formatDate1);

assert(negFormats.full.startsWith('-'), 'getAllFormats negative: full starts with -');
assert(negFormats.yearsDecimal.startsWith('-'), 'getAllFormats negative: yearsDecimal starts with -');
assert(negFormats.days.startsWith('-'), 'getAllFormats negative: days starts with -');
assert(negFormats.hours.startsWith('-'), 'getAllFormats negative: hours starts with -');
assert(negFormats.minutes.startsWith('-'), 'getAllFormats negative: minutes starts with -');
assert(negFormats.seconds.startsWith('-'), 'getAllFormats negative: seconds starts with -');

// Test specific known values
console.log('\n--- Specific Value Tests ---');

// 36 days, 3 hours, 30 minutes, 45 seconds
const specificDiff = DateCalculator.calculateDifference(formatDate1, formatDate2);
assert(specificDiff.totalDays === 36, 'specific: totalDays is 36');

// Test large date difference (historical)
console.log('\n--- Large Date Differences ---');
const moonLanding = new Date('1969-07-20T20:17:00Z');
const now2025 = new Date('2025-01-15T12:00:00Z');
const moonDiff = DateCalculator.calculateDifference(now2025, moonLanding);

assert(moonDiff.years > 50, 'historical: moon landing > 50 years ago');
assert(moonDiff.totalDays > 20000, 'historical: moon landing > 20000 days ago');
assert(moonDiff.isNegative === false, 'historical: not negative (now > past)');

// Summary
console.log('\n=== Results ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);

if (failed > 0) {
    process.exit(1);
}
