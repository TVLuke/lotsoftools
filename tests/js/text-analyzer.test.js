/**
 * Tests for Text Analyzer Library
 * Run with: node text-analyzer.test.js
 */

const TextAnalyzer = require('../../app/static/js/text-analyzer.js');

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

console.log('=== Text Analyzer Tests ===\n');

// Test countCharsWithSpaces
console.log('--- countCharsWithSpaces ---');

assert(TextAnalyzer.countCharsWithSpaces('hello') === 5, 'countCharsWithSpaces: simple word');
assert(TextAnalyzer.countCharsWithSpaces('hello world') === 11, 'countCharsWithSpaces: with space');
assert(TextAnalyzer.countCharsWithSpaces('') === 0, 'countCharsWithSpaces: empty string');
assert(TextAnalyzer.countCharsWithSpaces(null) === 0, 'countCharsWithSpaces: null');
assert(TextAnalyzer.countCharsWithSpaces('   ') === 3, 'countCharsWithSpaces: only spaces');

// Test countCharsWithoutSpaces
console.log('\n--- countCharsWithoutSpaces ---');

assert(TextAnalyzer.countCharsWithoutSpaces('hello') === 5, 'countCharsWithoutSpaces: simple word');
assert(TextAnalyzer.countCharsWithoutSpaces('hello world') === 10, 'countCharsWithoutSpaces: with space');
assert(TextAnalyzer.countCharsWithoutSpaces('') === 0, 'countCharsWithoutSpaces: empty string');
assert(TextAnalyzer.countCharsWithoutSpaces(null) === 0, 'countCharsWithoutSpaces: null');
assert(TextAnalyzer.countCharsWithoutSpaces('   ') === 0, 'countCharsWithoutSpaces: only spaces');
assert(TextAnalyzer.countCharsWithoutSpaces('a b\tc\nd') === 4, 'countCharsWithoutSpaces: various whitespace');

// Test countWords
console.log('\n--- countWords ---');

assert(TextAnalyzer.countWords('hello') === 1, 'countWords: single word');
assert(TextAnalyzer.countWords('hello world') === 2, 'countWords: two words');
assert(TextAnalyzer.countWords('one two three four five') === 5, 'countWords: five words');
assert(TextAnalyzer.countWords('') === 0, 'countWords: empty string');
assert(TextAnalyzer.countWords(null) === 0, 'countWords: null');
assert(TextAnalyzer.countWords('   ') === 0, 'countWords: only spaces');
assert(TextAnalyzer.countWords('  hello  world  ') === 2, 'countWords: extra spaces');
assert(TextAnalyzer.countWords('word\nanother\tthird') === 3, 'countWords: various whitespace');

// Test getWords
console.log('\n--- getWords ---');

let words = TextAnalyzer.getWords('hello world');
assert(words.length === 2, 'getWords: correct count');
assert(words[0] === 'hello', 'getWords: first word');
assert(words[1] === 'world', 'getWords: second word');

words = TextAnalyzer.getWords('');
assert(words.length === 0, 'getWords: empty string');

// Test getCharFrequency
console.log('\n--- getCharFrequency ---');

let freq = TextAnalyzer.getCharFrequency('aab');
assert(freq['a'] === 2, 'getCharFrequency: a count');
assert(freq['b'] === 1, 'getCharFrequency: b count');

freq = TextAnalyzer.getCharFrequency('hello');
assert(freq['l'] === 2, 'getCharFrequency: double letter');
assert(freq['h'] === 1, 'getCharFrequency: single letter');

freq = TextAnalyzer.getCharFrequency('');
assert(Object.keys(freq).length === 0, 'getCharFrequency: empty string');

// Test getWordFrequency
console.log('\n--- getWordFrequency ---');

freq = TextAnalyzer.getWordFrequency('the cat and the dog');
assert(freq['the'] === 2, 'getWordFrequency: repeated word');
assert(freq['cat'] === 1, 'getWordFrequency: single word');

freq = TextAnalyzer.getWordFrequency('Hello HELLO hello');
assert(freq['hello'] === 3, 'getWordFrequency: case insensitive');

freq = TextAnalyzer.getWordFrequency('');
assert(Object.keys(freq).length === 0, 'getWordFrequency: empty string');

// Test getSortedCharFrequency
console.log('\n--- getSortedCharFrequency ---');

let sorted = TextAnalyzer.getSortedCharFrequency('aabbbcccc');
assert(sorted[0][0] === 'c', 'getSortedCharFrequency: most frequent first');
assert(sorted[0][1] === 4, 'getSortedCharFrequency: correct count');
assert(sorted[1][0] === 'b', 'getSortedCharFrequency: second most frequent');
assert(sorted[2][0] === 'a', 'getSortedCharFrequency: third most frequent');

// Test getSortedWordFrequency
console.log('\n--- getSortedWordFrequency ---');

sorted = TextAnalyzer.getSortedWordFrequency('a a a b b c');
assert(sorted[0][0] === 'a', 'getSortedWordFrequency: most frequent first');
assert(sorted[0][1] === 3, 'getSortedWordFrequency: correct count');
assert(sorted[1][0] === 'b', 'getSortedWordFrequency: second most frequent');
assert(sorted[2][0] === 'c', 'getSortedWordFrequency: third');

// Test limit
sorted = TextAnalyzer.getSortedWordFrequency('a b c d e f g h i j k', 5);
assert(sorted.length === 5, 'getSortedWordFrequency: respects limit');

// Test analyze
console.log('\n--- analyze ---');

const result = TextAnalyzer.analyze('Hello World');
assert(result.charsWithSpaces === 11, 'analyze: charsWithSpaces');
assert(result.charsWithoutSpaces === 10, 'analyze: charsWithoutSpaces');
assert(result.wordCount === 2, 'analyze: wordCount');
assert(Array.isArray(result.charFrequency), 'analyze: charFrequency is array');
assert(Array.isArray(result.wordFrequency), 'analyze: wordFrequency is array');

// Summary
console.log('\n=== Test Summary ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log(`Total: ${passed + failed}`);

process.exit(failed > 0 ? 1 : 0);
