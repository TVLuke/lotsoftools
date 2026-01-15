/**
 * Text Analyzer Library
 * Provides functions to count characters, words, and analyze frequency.
 */

const TextAnalyzer = (function() {
    'use strict';

    /**
     * Count characters with spaces
     * @param {string} text - Input text
     * @returns {number}
     */
    function countCharsWithSpaces(text) {
        if (!text) return 0;
        return text.length;
    }

    /**
     * Count characters without spaces
     * @param {string} text - Input text
     * @returns {number}
     */
    function countCharsWithoutSpaces(text) {
        if (!text) return 0;
        return text.replace(/\s/g, '').length;
    }

    /**
     * Count words in text
     * @param {string} text - Input text
     * @returns {number}
     */
    function countWords(text) {
        if (!text || !text.trim()) return 0;
        return text.trim().split(/\s+/).filter(word => word.length > 0).length;
    }

    /**
     * Get word list from text
     * @param {string} text - Input text
     * @returns {string[]}
     */
    function getWords(text) {
        if (!text || !text.trim()) return [];
        return text.trim().split(/\s+/).filter(word => word.length > 0);
    }

    /**
     * Get character frequency map
     * @param {string} text - Input text
     * @returns {Object} Map of character to count
     */
    function getCharFrequency(text) {
        if (!text) return {};
        
        const charMap = {};
        for (let char of text) {
            if (charMap[char]) {
                charMap[char]++;
            } else {
                charMap[char] = 1;
            }
        }
        return charMap;
    }

    /**
     * Get word frequency map (case-insensitive)
     * @param {string} text - Input text
     * @returns {Object} Map of word to count
     */
    function getWordFrequency(text) {
        const words = getWords(text);
        const wordMap = {};
        
        for (let word of words) {
            const lowerWord = word.toLowerCase();
            if (wordMap[lowerWord]) {
                wordMap[lowerWord]++;
            } else {
                wordMap[lowerWord] = 1;
            }
        }
        return wordMap;
    }

    /**
     * Get sorted character frequency (descending by count)
     * @param {string} text - Input text
     * @returns {Array} Array of [char, count] pairs
     */
    function getSortedCharFrequency(text) {
        const charMap = getCharFrequency(text);
        return Object.entries(charMap).sort((a, b) => b[1] - a[1]);
    }

    /**
     * Get sorted word frequency (descending by count)
     * @param {string} text - Input text
     * @param {number} limit - Max results (default: 100)
     * @returns {Array} Array of [word, count] pairs
     */
    function getSortedWordFrequency(text, limit) {
        if (limit === undefined) limit = 100;
        const wordMap = getWordFrequency(text);
        return Object.entries(wordMap).sort((a, b) => b[1] - a[1]).slice(0, limit);
    }

    /**
     * Analyze text and return all stats
     * @param {string} text - Input text
     * @returns {Object}
     */
    function analyze(text) {
        return {
            charsWithSpaces: countCharsWithSpaces(text),
            charsWithoutSpaces: countCharsWithoutSpaces(text),
            wordCount: countWords(text),
            charFrequency: getSortedCharFrequency(text),
            wordFrequency: getSortedWordFrequency(text)
        };
    }

    // Public API
    return {
        countCharsWithSpaces: countCharsWithSpaces,
        countCharsWithoutSpaces: countCharsWithoutSpaces,
        countWords: countWords,
        getWords: getWords,
        getCharFrequency: getCharFrequency,
        getWordFrequency: getWordFrequency,
        getSortedCharFrequency: getSortedCharFrequency,
        getSortedWordFrequency: getSortedWordFrequency,
        analyze: analyze
    };
})();

// Export for Node.js testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TextAnalyzer;
}
