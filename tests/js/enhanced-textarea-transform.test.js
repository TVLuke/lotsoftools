/**
 * Tests for Enhanced Textarea - Text Transformations
 * Run with: node enhanced-textarea-transform.test.js
 */

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

function assertEqual(actual, expected, message) {
    if (actual === expected) {
        passed++;
        console.log(`✓ ${message}`);
    } else {
        failed++;
        console.log(`✗ ${message}`);
        console.log(`  Expected: "${expected}"`);
        console.log(`  Actual:   "${actual}"`);
    }
}

// Transform functions extracted from enhanced-textarea.js for testing
const transforms = {
    lowercase: (text) => text.toLowerCase(),
    uppercase: (text) => text.toUpperCase(),
    sortlines: (text) => text.split('\n').sort((a, b) => a.localeCompare(b)).join('\n'),
    'linebreaks-to-spaces': (text) => text.replace(/\r?\n/g, ' '),
    trim: (text) => text.trim(),
    'remove-whitespace': (text) => text.replace(/\s+/g, '')
};

console.log('=== Enhanced Textarea Transform Tests ===\n');

// Test lowercase
console.log('--- lowercase ---');
assertEqual(transforms.lowercase('HELLO WORLD'), 'hello world', 'lowercase: all caps');
assertEqual(transforms.lowercase('Hello World'), 'hello world', 'lowercase: mixed case');
assertEqual(transforms.lowercase('already lowercase'), 'already lowercase', 'lowercase: already lowercase');
assertEqual(transforms.lowercase(''), '', 'lowercase: empty string');
assertEqual(transforms.lowercase('123 ABC xyz'), '123 abc xyz', 'lowercase: mixed with numbers');
assertEqual(transforms.lowercase('ÜBER MÜNCHEN'), 'über münchen', 'lowercase: German umlauts');

// Test uppercase
console.log('\n--- uppercase ---');
assertEqual(transforms.uppercase('hello world'), 'HELLO WORLD', 'uppercase: all lowercase');
assertEqual(transforms.uppercase('Hello World'), 'HELLO WORLD', 'uppercase: mixed case');
assertEqual(transforms.uppercase('ALREADY UPPERCASE'), 'ALREADY UPPERCASE', 'uppercase: already uppercase');
assertEqual(transforms.uppercase(''), '', 'uppercase: empty string');
assertEqual(transforms.uppercase('123 abc XYZ'), '123 ABC XYZ', 'uppercase: mixed with numbers');
assertEqual(transforms.uppercase('über münchen'), 'ÜBER MÜNCHEN', 'uppercase: German umlauts');

// Test sortlines
console.log('\n--- sortlines ---');
assertEqual(transforms.sortlines('banana\napple\ncherry'), 'apple\nbanana\ncherry', 'sortlines: alphabetical');
assertEqual(transforms.sortlines('zebra\nalpha\nmango'), 'alpha\nmango\nzebra', 'sortlines: another order');
assertEqual(transforms.sortlines('single line'), 'single line', 'sortlines: single line');
assertEqual(transforms.sortlines(''), '', 'sortlines: empty string');
assertEqual(transforms.sortlines('B\na\nC'), 'a\nB\nC', 'sortlines: locale-aware sorting');
assertEqual(transforms.sortlines('3\n1\n2'), '1\n2\n3', 'sortlines: numbers as strings');
assertEqual(transforms.sortlines('line\n\nanother'), '\nanother\nline', 'sortlines: with empty line');

// Test linebreaks-to-spaces
console.log('\n--- linebreaks-to-spaces ---');
assertEqual(transforms['linebreaks-to-spaces']('hello\nworld'), 'hello world', 'linebreaks-to-spaces: unix newline');
assertEqual(transforms['linebreaks-to-spaces']('hello\r\nworld'), 'hello world', 'linebreaks-to-spaces: windows newline');
assertEqual(transforms['linebreaks-to-spaces']('one\ntwo\nthree'), 'one two three', 'linebreaks-to-spaces: multiple newlines');
assertEqual(transforms['linebreaks-to-spaces']('no newlines'), 'no newlines', 'linebreaks-to-spaces: no newlines');
assertEqual(transforms['linebreaks-to-spaces'](''), '', 'linebreaks-to-spaces: empty string');
assertEqual(transforms['linebreaks-to-spaces']('\n\n\n'), '   ', 'linebreaks-to-spaces: only newlines');

// Test trim
console.log('\n--- trim ---');
assertEqual(transforms.trim('  hello  '), 'hello', 'trim: spaces both sides');
assertEqual(transforms.trim('hello'), 'hello', 'trim: no spaces');
assertEqual(transforms.trim('   hello'), 'hello', 'trim: leading spaces');
assertEqual(transforms.trim('hello   '), 'hello', 'trim: trailing spaces');
assertEqual(transforms.trim(''), '', 'trim: empty string');
assertEqual(transforms.trim('   '), '', 'trim: only spaces');
assertEqual(transforms.trim('\n\nhello\n\n'), 'hello', 'trim: newlines');
assertEqual(transforms.trim('\t\thello\t\t'), 'hello', 'trim: tabs');
assertEqual(transforms.trim('  hello  world  '), 'hello  world', 'trim: preserves inner spaces');

// Test remove-whitespace
console.log('\n--- remove-whitespace ---');
assertEqual(transforms['remove-whitespace']('hello world'), 'helloworld', 'remove-whitespace: removes spaces');
assertEqual(transforms['remove-whitespace']('hello\nworld'), 'helloworld', 'remove-whitespace: removes newlines');
assertEqual(transforms['remove-whitespace']('hello\tworld'), 'helloworld', 'remove-whitespace: removes tabs');
assertEqual(transforms['remove-whitespace']('  hello  world  '), 'helloworld', 'remove-whitespace: multiple spaces');
assertEqual(transforms['remove-whitespace']('hello'), 'hello', 'remove-whitespace: no whitespace');
assertEqual(transforms['remove-whitespace'](''), '', 'remove-whitespace: empty string');
assertEqual(transforms['remove-whitespace']('   '), '', 'remove-whitespace: only spaces');
assertEqual(transforms['remove-whitespace']('a b\nc\td'), 'abcd', 'remove-whitespace: mixed whitespace');

// Test combinations / edge cases
console.log('\n--- edge cases ---');
assertEqual(transforms.lowercase(transforms.trim('  HELLO WORLD  ')), 'hello world', 'combo: trim then lowercase');
assertEqual(transforms.uppercase(transforms.trim('  hello world  ')), 'HELLO WORLD', 'combo: trim then uppercase');
assertEqual(transforms['remove-whitespace'](transforms.sortlines('b\na\nc')), 'abc', 'combo: sort then remove whitespace');

// Summary
console.log('\n=== Test Summary ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log(`Total: ${passed + failed}`);

process.exit(failed > 0 ? 1 : 0);
