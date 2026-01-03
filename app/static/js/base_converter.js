/**
 * Base Converter Library
 * Converts numbers between different numeral systems (bases)
 * Works in both browser and Node.js environments
 */

(function(root, factory) {
    if (typeof module === 'object' && module.exports) {
        // Node.js
        module.exports = factory();
    } else {
        // Browser
        root.BaseConverter = factory();
    }
}(typeof self !== 'undefined' ? self : this, function() {
    'use strict';

    // Default symbols: 0-9, A-Z, then Greek letters
    const DEFAULT_SYMBOLS = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
        'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
        'U', 'V', 'W', 'X', 'Y', 'Z',
        'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ',
        'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ',
        'φ', 'χ', 'ψ', 'ω'
    ];

    /**
     * Get default symbols for a given base
     * @param {number} base - The base (2-62+)
     * @returns {string[]} Array of symbols for the base
     */
    function getDefaultSymbols(base) {
        if (base <= DEFAULT_SYMBOLS.length) {
            return DEFAULT_SYMBOLS.slice(0, base);
        }
        return null; // Not enough default symbols
    }

    /**
     * Validate that symbols are valid for a given base
     * @param {string[]} symbols - Array of symbol strings
     * @param {number} base - The base
     * @returns {{valid: boolean, error: string|null}}
     */
    function validateSymbols(symbols, base) {
        if (!Array.isArray(symbols)) {
            return { valid: false, error: 'Symbols must be an array' };
        }
        
        if (symbols.length !== base) {
            return { 
                valid: false, 
                error: `Number of symbols (${symbols.length}) must match base (${base})` 
            };
        }

        // Check for duplicates (case-insensitive)
        const upperSymbols = symbols.map(s => s.toUpperCase());
        const uniqueUpper = new Set(upperSymbols);
        if (uniqueUpper.size !== symbols.length) {
            return { valid: false, error: 'Symbols must be unique (no duplicates)' };
        }

        // Check for empty symbols
        if (symbols.some(s => !s || s.length === 0)) {
            return { valid: false, error: 'Symbols cannot be empty' };
        }

        return { valid: true, error: null };
    }

    /**
     * Convert a number string from a given base to decimal (BigInt)
     * @param {string} str - The number string to convert
     * @param {number} fromBase - The base of the input number
     * @param {string[]} symbols - The symbols used for the base
     * @returns {{value: BigInt|null, error: string|null}}
     */
    function toDecimal(str, fromBase, symbols) {
        if (!str || str.length === 0) {
            return { value: null, error: 'Input string is empty' };
        }

        if (fromBase < 2) {
            return { value: null, error: 'Base must be at least 2' };
        }

        const validation = validateSymbols(symbols, fromBase);
        if (!validation.valid) {
            return { value: null, error: validation.error };
        }

        const upperSymbols = symbols.map(s => s.toUpperCase());
        let result = 0n;
        const base = BigInt(fromBase);

        for (let i = 0; i < str.length; i++) {
            const char = str[i].toUpperCase();
            const value = upperSymbols.indexOf(char);

            if (value === -1) {
                return { 
                    value: null, 
                    error: `Invalid character '${str[i]}' for base ${fromBase}` 
                };
            }

            result = result * base + BigInt(value);
        }

        return { value: result, error: null };
    }

    /**
     * Convert a decimal (BigInt) to a string in the target base
     * @param {BigInt} decimal - The decimal number to convert
     * @param {number} toBase - The target base
     * @param {string[]} symbols - The symbols to use for the target base
     * @returns {{value: string|null, error: string|null}}
     */
    function fromDecimal(decimal, toBase, symbols) {
        if (decimal === null || decimal === undefined) {
            return { value: null, error: 'Input is null or undefined' };
        }

        if (toBase < 2) {
            return { value: null, error: 'Base must be at least 2' };
        }

        const validation = validateSymbols(symbols, toBase);
        if (!validation.valid) {
            return { value: null, error: validation.error };
        }

        // Handle BigInt conversion
        let num;
        try {
            num = BigInt(decimal);
        } catch (e) {
            return { value: null, error: 'Invalid decimal value' };
        }

        if (num === 0n) {
            return { value: symbols[0], error: null };
        }

        if (num < 0n) {
            return { value: null, error: 'Negative numbers not supported' };
        }

        let result = '';
        const base = BigInt(toBase);

        while (num > 0n) {
            const remainder = Number(num % base);
            result = symbols[remainder] + result;
            num = num / base;
        }

        return { value: result, error: null };
    }

    /**
     * Convert a number string from one base to another
     * @param {string} str - The number string to convert
     * @param {number} fromBase - The source base
     * @param {number} toBase - The target base
     * @param {string[]} [fromSymbols] - Symbols for source base (optional, uses defaults)
     * @param {string[]} [toSymbols] - Symbols for target base (optional, uses defaults)
     * @returns {{value: string|null, error: string|null}}
     */
    function convert(str, fromBase, toBase, fromSymbols, toSymbols) {
        // Use default symbols if not provided
        const srcSymbols = fromSymbols || getDefaultSymbols(fromBase);
        const dstSymbols = toSymbols || getDefaultSymbols(toBase);

        if (!srcSymbols) {
            return { value: null, error: `No default symbols for base ${fromBase}. Please provide custom symbols.` };
        }
        if (!dstSymbols) {
            return { value: null, error: `No default symbols for base ${toBase}. Please provide custom symbols.` };
        }

        // Convert to decimal first
        const decimalResult = toDecimal(str, fromBase, srcSymbols);
        if (decimalResult.error) {
            return { value: null, error: decimalResult.error };
        }

        // Convert from decimal to target base
        return fromDecimal(decimalResult.value, toBase, dstSymbols);
    }

    /**
     * Filter a string to only include valid symbols for a base
     * @param {string} str - The input string
     * @param {number} base - The base
     * @param {string[]} [symbols] - The symbols (optional, uses defaults)
     * @returns {string} Filtered string with only valid characters
     */
    function filterToValidSymbols(str, base, symbols) {
        const validSymbols = symbols || getDefaultSymbols(base);
        if (!validSymbols) return '';

        const upperSymbols = validSymbols.map(s => s.toUpperCase());
        let filtered = '';

        for (const char of str) {
            const upperChar = char.toUpperCase();
            const idx = upperSymbols.indexOf(upperChar);
            if (idx !== -1) {
                // Use the symbol from the defined set (preserves case)
                filtered += validSymbols[idx];
            }
        }

        return filtered;
    }

    /**
     * Check if a string is valid for a given base
     * @param {string} str - The string to check
     * @param {number} base - The base
     * @param {string[]} [symbols] - The symbols (optional, uses defaults)
     * @returns {boolean}
     */
    function isValidForBase(str, base, symbols) {
        const validSymbols = symbols || getDefaultSymbols(base);
        if (!validSymbols) return false;

        const upperSymbols = validSymbols.map(s => s.toUpperCase());

        for (const char of str) {
            if (upperSymbols.indexOf(char.toUpperCase()) === -1) {
                return false;
            }
        }

        return true;
    }

    /**
     * Parse a comma-separated string into an array of symbols
     * @param {string} str - Comma-separated symbols string
     * @returns {string[]} Array of symbols
     */
    function parseSymbolsString(str) {
        if (!str || str.trim() === '') {
            return [];
        }
        return str.split(',').map(s => s.trim()).filter(s => s.length > 0);
    }

    // Public API
    return {
        DEFAULT_SYMBOLS: DEFAULT_SYMBOLS,
        getDefaultSymbols: getDefaultSymbols,
        validateSymbols: validateSymbols,
        toDecimal: toDecimal,
        fromDecimal: fromDecimal,
        convert: convert,
        filterToValidSymbols: filterToValidSymbols,
        isValidForBase: isValidForBase,
        parseSymbolsString: parseSymbolsString
    };
}));
