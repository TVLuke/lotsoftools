/**
 * Tests for JSON Formatter Library
 * Run with: node json-formatter.test.js
 */

const JsonFormatter = require('../../app/static/js/json-formatter.js');
const fs = require('fs');
const path = require('path');

const DUMMY_DATA_DIR = path.join(__dirname, 'static', 'json-dummy-data');

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

console.log('=== JSON Formatter Tests ===\n');

// Test validate
console.log('--- validate ---');

let result = JsonFormatter.validate('{"name": "test"}');
assert(result.valid === true, 'validate: valid JSON object');
assert(result.data.name === 'test', 'validate: parsed data correctly');

result = JsonFormatter.validate('[1, 2, 3]');
assert(result.valid === true, 'validate: valid JSON array');

result = JsonFormatter.validate('invalid json');
assert(result.valid === false, 'validate: invalid JSON returns false');
assert(result.error !== null, 'validate: error message provided');

result = JsonFormatter.validate('');
assert(result.valid === false, 'validate: empty string returns false');

result = JsonFormatter.validate('   ');
assert(result.valid === false, 'validate: whitespace only returns false');

result = JsonFormatter.validate(null);
assert(result.valid === false, 'validate: null returns false');

// Test format
console.log('\n--- format ---');

result = JsonFormatter.format('{"a":1,"b":2}', 2);
assert(result.success === true, 'format: success on valid JSON');
assert(result.output.includes('\n'), 'format: output has newlines');
assert(result.output.includes('  '), 'format: output has indentation');

result = JsonFormatter.format('{"a":1}', 4);
assert(result.output.includes('    '), 'format: 4-space indentation works');

result = JsonFormatter.format('{"a":1}', '\t');
assert(result.output.includes('\t'), 'format: tab indentation works');

result = JsonFormatter.format('invalid');
assert(result.success === false, 'format: fails on invalid JSON');
assert(result.error !== null, 'format: provides error on invalid JSON');

// Test format produces correct output
const unformatted = '{"name":"John","age":30,"city":"New York"}';
result = JsonFormatter.format(unformatted, 2);
const expected = `{
  "name": "John",
  "age": 30,
  "city": "New York"
}`;
assert(result.output === expected, 'format: produces correct formatted output');

// Test minify
console.log('\n--- minify ---');

result = JsonFormatter.minify('{\n  "a": 1,\n  "b": 2\n}');
assert(result.success === true, 'minify: success on valid JSON');
assert(result.output === '{"a": 1,"b": 2}', 'minify: removes whitespace but keeps space after colon');

result = JsonFormatter.minify('invalid');
assert(result.success === false, 'minify: fails on invalid JSON');

// Test edge cases
console.log('\n--- edge cases ---');

result = JsonFormatter.validate('null');
assert(result.valid === true, 'edge case: null literal is valid JSON');

result = JsonFormatter.validate('true');
assert(result.valid === true, 'edge case: boolean literal is valid JSON');

result = JsonFormatter.validate('123');
assert(result.valid === true, 'edge case: number literal is valid JSON');

result = JsonFormatter.validate('"string"');
assert(result.valid === true, 'edge case: string literal is valid JSON');

result = JsonFormatter.format('{"nested":{"a":{"b":1}}}', 2);
assert(result.success === true, 'edge case: nested objects format correctly');

// Test with dummy data files
console.log('\n--- dummy data files ---');

// Helper: check if two JSON strings are semantically equivalent
function jsonEqual(a, b) {
    return JSON.stringify(JSON.parse(a)) === JSON.stringify(JSON.parse(b));
}

// Test formatting min.json produces equivalent JSON
const minFile64 = fs.readFileSync(path.join(DUMMY_DATA_DIR, '64KB-min.json'), 'utf8');
const formattedFile64 = fs.readFileSync(path.join(DUMMY_DATA_DIR, '64KB.json'), 'utf8');
result = JsonFormatter.format(minFile64, 2);
assert(result.success === true, 'dummy data: 64KB-min.json formats successfully');
assert(jsonEqual(result.output, formattedFile64), 'dummy data: 64KB-min.json formats to equivalent JSON');

// Test minifying formatted produces equivalent JSON
result = JsonFormatter.minify(formattedFile64);
assert(result.success === true, 'dummy data: 64KB.json minifies successfully');
assert(jsonEqual(result.output, minFile64), 'dummy data: 64KB.json minifies to equivalent JSON');

// Test round-trip consistency
const formatted = JsonFormatter.format(minFile64, 2).output;
const minified = JsonFormatter.minify(formatted).output;
const reformatted = JsonFormatter.format(minified, 2).output;
assert(formatted === reformatted, 'dummy data: 64KB round-trip is consistent');

// Test with 128KB file
const minFile128 = fs.readFileSync(path.join(DUMMY_DATA_DIR, '128KB-min.json'), 'utf8');
const formattedFile128 = fs.readFileSync(path.join(DUMMY_DATA_DIR, '128KB.json'), 'utf8');
result = JsonFormatter.format(minFile128, 2);
assert(result.success === true, 'dummy data: 128KB-min.json formats successfully');
assert(jsonEqual(result.output, formattedFile128), 'dummy data: 128KB-min.json formats to equivalent JSON');

result = JsonFormatter.minify(formattedFile128);
assert(result.success === true, 'dummy data: 128KB.json minifies successfully');
assert(jsonEqual(result.output, minFile128), 'dummy data: 128KB.json minifies to equivalent JSON');

// Test invalid JSON files
console.log('\n--- invalid JSON files ---');

const missingColon = fs.readFileSync(path.join(DUMMY_DATA_DIR, 'missing-colon.json'), 'utf8');
result = JsonFormatter.validate(missingColon);
assert(result.valid === false, 'invalid: missing-colon.json detected as invalid');

const unterminated = fs.readFileSync(path.join(DUMMY_DATA_DIR, 'unterminated.json'), 'utf8');
result = JsonFormatter.validate(unterminated);
assert(result.valid === false, 'invalid: unterminated.json detected as invalid');

// binary-data.json test (if file exists)
const binaryDataPath = path.join(DUMMY_DATA_DIR, 'binary-data.json');
if (fs.existsSync(binaryDataPath)) {
    const binaryData = fs.readFileSync(binaryDataPath, 'utf8');
    result = JsonFormatter.validate(binaryData);
    assert(result.valid === false, 'invalid: binary-data.json detected as invalid');
}

// Summary
console.log('\n=== Test Summary ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log(`Total: ${passed + failed}`);

process.exit(failed > 0 ? 1 : 0);
