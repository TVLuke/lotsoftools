/**
 * Tests for Holiday Calendar Utility Functions
 * Run with: node holiday-calendar.test.js
 */

const HolidayCalendar = require('../../app/static/js/holiday-calendar.js');

let passed = 0;
let failed = 0;

function assert(condition, message) {
    if (condition) {
        passed++;
        console.log(`✓ ${message}`);
    } else {
        failed++;
        console.log(`✗ ${message}`);
    }
}

console.log('=== Holiday Calendar Tests ===\n');

// Test getLabels
console.log('--- getLabels ---');

let labels = HolidayCalendar.getLabels('de');
assert(labels.all === 'Alle', 'getLabels: German "all" label');
assert(labels.publicHoliday === 'Feiertag', 'getLabels: German "publicHoliday" label');

labels = HolidayCalendar.getLabels('en');
assert(labels.all === 'All', 'getLabels: English "all" label');
assert(labels.publicHoliday === 'Public Holiday', 'getLabels: English "publicHoliday" label');

labels = HolidayCalendar.getLabels('xyz');
assert(labels.all === 'All', 'getLabels: Unknown language falls back to English');

labels = HolidayCalendar.getLabels('DE');
assert(labels.all === 'Alle', 'getLabels: Handles uppercase language codes');

// Test getLocale
console.log('\n--- getLocale ---');

assert(HolidayCalendar.getLocale('DE') === 'de-DE', 'getLocale: DE returns de-DE');
assert(HolidayCalendar.getLocale('EN') === 'en-GB', 'getLocale: EN returns en-GB');
assert(HolidayCalendar.getLocale('FR') === 'fr-FR', 'getLocale: FR returns fr-FR');
assert(HolidayCalendar.getLocale('XY') === 'en-GB', 'getLocale: Unknown returns en-GB');

// Test formatDate
console.log('\n--- formatDate ---');

let result = HolidayCalendar.formatDate('2026-01-15', 'en-GB');
assert(result.includes('15'), 'formatDate: Contains day');
assert(result.includes('2026'), 'formatDate: Contains year');

assert(HolidayCalendar.formatDate(null, 'en-GB') === '', 'formatDate: null returns empty string');
assert(HolidayCalendar.formatDate(undefined, 'en-GB') === '', 'formatDate: undefined returns empty string');

// Test formatDateRange
console.log('\n--- formatDateRange ---');

result = HolidayCalendar.formatDateRange('2026-01-15', '2026-01-15', 'en-GB');
assert(result.includes('15'), 'formatDateRange: Same date contains day');
assert(result.includes('2026'), 'formatDateRange: Same date contains year');

result = HolidayCalendar.formatDateRange('2026-01-15', '2026-01-20', 'en-GB');
assert(result.includes('15'), 'formatDateRange: Range contains start day');
assert(result.includes('20'), 'formatDateRange: Range contains end day');
assert(result.includes('–'), 'formatDateRange: Range contains dash');

assert(HolidayCalendar.formatDateRange(null, '2026-01-20', 'en-GB') === '', 'formatDateRange: null start returns empty');

result = HolidayCalendar.formatDateRange('2026-01-15', null, 'en-GB');
assert(result.includes('15'), 'formatDateRange: null end formats as single date');

// Test filterHolidaysByYear
console.log('\n--- filterHolidaysByYear ---');

const holidays = [
    { start_date: '2025-12-24', end_date: '2025-12-26', name: 'Christmas 2025' },
    { start_date: '2026-01-01', end_date: '2026-01-01', name: 'New Year 2026' },
    { start_date: '2026-12-31', end_date: '2027-01-02', name: 'New Year 2027' },
    { start_date: '2027-05-01', end_date: '2027-05-01', name: 'May Day 2027' }
];

result = HolidayCalendar.filterHolidaysByYear(holidays, 'all');
assert(result.length === 4, 'filterHolidaysByYear: "all" returns all holidays');

result = HolidayCalendar.filterHolidaysByYear(holidays, 2026);
assert(result.length === 2, 'filterHolidaysByYear: 2026 returns 2 holidays');
assert(result[0].name === 'New Year 2026', 'filterHolidaysByYear: First is New Year 2026');

result = HolidayCalendar.filterHolidaysByYear(holidays, 2027);
assert(result.length === 2, 'filterHolidaysByYear: 2027 returns 2 holidays');
assert(result.some(h => h.name === 'New Year 2027'), 'filterHolidaysByYear: Includes spanning holiday');
assert(result.some(h => h.name === 'May Day 2027'), 'filterHolidaysByYear: Includes May Day 2027');

result = HolidayCalendar.filterHolidaysByYear(holidays, '2026');
assert(result.length === 2, 'filterHolidaysByYear: String year works');

result = HolidayCalendar.filterHolidaysByYear(holidays, null);
assert(result.length === 4, 'filterHolidaysByYear: null returns all');

// Test getHolidayMap
console.log('\n--- getHolidayMap ---');

const mapHolidays = [
    { start_date: '2026-01-01', end_date: '2026-01-02', type: 'public' },
    { start_date: '2026-01-05', end_date: '2026-01-07', type: 'school' }
];

let map = HolidayCalendar.getHolidayMap(mapHolidays, 2026);
assert(map['2026-01-01'].public === true, 'getHolidayMap: Jan 1 is public');
assert(map['2026-01-01'].school === false, 'getHolidayMap: Jan 1 is not school');
assert(map['2026-01-05'].school === true, 'getHolidayMap: Jan 5 is school');
assert(map['2026-01-06'].school === true, 'getHolidayMap: Jan 6 is school (middle of range)');

const crossYearHolidays = [
    { start_date: '2025-12-30', end_date: '2026-01-02', type: 'school' }
];
map = HolidayCalendar.getHolidayMap(crossYearHolidays, 2026);
assert(map['2025-12-30'] === undefined, 'getHolidayMap: Does not include dates outside year');
assert(map['2026-01-01'].school === true, 'getHolidayMap: Includes dates in year');

// Test getWeekNumber
console.log('\n--- getWeekNumber ---');

let week = HolidayCalendar.getWeekNumber(new Date(2026, 0, 1));
assert(week === 1, 'getWeekNumber: Jan 1, 2026 is week 1');

week = HolidayCalendar.getWeekNumber(new Date(2026, 5, 15));
assert(week >= 24 && week <= 25, 'getWeekNumber: June 15, 2026 is around week 25');

// Test getMonthNames
console.log('\n--- getMonthNames ---');

let months = HolidayCalendar.getMonthNames('de');
assert(months[0] === 'Januar', 'getMonthNames: German January');
assert(months[11] === 'Dezember', 'getMonthNames: German December');

months = HolidayCalendar.getMonthNames('xyz');
assert(months[0] === 'January', 'getMonthNames: Unknown falls back to English');

// Test getDayNamesShort
console.log('\n--- getDayNamesShort ---');

let days = HolidayCalendar.getDayNamesShort('de');
assert(days[0] === 'Mo', 'getDayNamesShort: German Monday');
assert(days[6] === 'So', 'getDayNamesShort: German Sunday');

days = HolidayCalendar.getDayNamesShort('en');
assert(days[0] === 'Mo', 'getDayNamesShort: English Monday');
assert(days[6] === 'Su', 'getDayNamesShort: English Sunday');

// Summary
console.log('\n=== Results ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);

if (failed > 0) {
    process.exit(1);
}
