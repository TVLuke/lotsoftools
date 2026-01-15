/**
 * Tests for JSON Formatter Library
 * Run with: node json-formatter.test.js
 */

const JsonFormatter = require('../../app/static/js/json-formatter.js');

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
assert(result.output === '{"a":1,"b":2}', 'minify: removes whitespace');

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

// Summary
console.log('\n=== Test Summary ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log(`Total: ${passed + failed}`);

process.exit(failed > 0 ? 1 : 0);
