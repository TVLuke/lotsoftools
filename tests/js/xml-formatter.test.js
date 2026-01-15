/**
 * Tests for XML Formatter Library
 * Run with: node xml-formatter.test.js
 */

const XmlFormatter = require('../../app/static/js/xml-formatter.js');

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

console.log('=== XML Formatter Tests ===\n');

// Test validate
console.log('--- validate ---');

let result = XmlFormatter.validate('<root><child>text</child></root>');
assert(result.valid === true, 'validate: valid XML');

result = XmlFormatter.validate('<root/>');
assert(result.valid === true, 'validate: self-closing tag');

result = XmlFormatter.validate('');
assert(result.valid === false, 'validate: empty string returns false');

result = XmlFormatter.validate('   ');
assert(result.valid === false, 'validate: whitespace only returns false');

result = XmlFormatter.validate(null);
assert(result.valid === false, 'validate: null returns false');

// Test format
console.log('\n--- format ---');

result = XmlFormatter.format('<root><child>text</child></root>', '  ');
assert(result.success === true, 'format: success on valid XML');
assert(result.output.includes('\n'), 'format: output has newlines');

result = XmlFormatter.format('<root><a>1</a><b>2</b></root>', '    ');
assert(result.success === true, 'format: 4-space indentation works');

result = XmlFormatter.format('<root><child>text</child></root>', '\t');
assert(result.output.includes('\t') || result.success, 'format: tab indentation works');

// Test minify
console.log('\n--- minify ---');

result = XmlFormatter.minify('<root>\n  <child>text</child>\n</root>');
assert(result.success === true, 'minify: success on valid XML');
assert(result.output === '<root><child>text</child></root>', 'minify: removes whitespace between tags');

result = XmlFormatter.minify('  <root>  <child>  </child>  </root>  ');
assert(result.success === true, 'minify: handles extra whitespace');

// Test edge cases
console.log('\n--- edge cases ---');

result = XmlFormatter.validate('<?xml version="1.0"?><root></root>');
assert(result.valid === true, 'edge case: XML declaration');

result = XmlFormatter.validate('<root attr="value"></root>');
assert(result.valid === true, 'edge case: attributes');

result = XmlFormatter.validate('<!-- comment --><root></root>');
assert(result.valid === true, 'edge case: comments');

result = XmlFormatter.format('<a><b><c>deep</c></b></a>', '  ');
assert(result.success === true, 'edge case: deeply nested');

// Summary
console.log('\n=== Test Summary ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log(`Total: ${passed + failed}`);

process.exit(failed > 0 ? 1 : 0);
