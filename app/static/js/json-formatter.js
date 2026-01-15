/**
 * JSON Formatter Library
 * Provides functions to validate, format, and minify JSON.
 */

const JsonFormatter = (function() {
    'use strict';

    /**
     * Validate JSON string
     * @param {string} input - JSON string to validate
     * @returns {{valid: boolean, data: any, error: string|null}}
     */
    function validate(input) {
        if (!input || !input.trim()) {
            return { valid: false, data: null, error: 'Empty input' };
        }
        
        try {
            const data = JSON.parse(input);
            return { valid: true, data: data, error: null };
        } catch (e) {
            return { valid: false, data: null, error: e.message };
        }
    }

    /**
     * Format JSON string with indentation
     * @param {string} input - JSON string to format
     * @param {number|string} indent - Number of spaces or '\t' for tabs
     * @returns {{success: boolean, output: string, error: string|null}}
     */
    function format(input, indent) {
        if (indent === undefined) indent = 2;
        
        const validation = validate(input);
        if (!validation.valid) {
            return { success: false, output: '', error: validation.error };
        }
        
        try {
            const output = JSON.stringify(validation.data, null, indent);
            return { success: true, output: output, error: null };
        } catch (e) {
            return { success: false, output: '', error: e.message };
        }
    }

    /**
     * Minify JSON string (remove whitespace)
     * @param {string} input - JSON string to minify
     * @returns {{success: boolean, output: string, error: string|null}}
     */
    function minify(input) {
        const validation = validate(input);
        if (!validation.valid) {
            return { success: false, output: '', error: validation.error };
        }
        
        try {
            const output = JSON.stringify(validation.data);
            return { success: true, output: output, error: null };
        } catch (e) {
            return { success: false, output: '', error: e.message };
        }
    }

    // Public API
    return {
        validate: validate,
        format: format,
        minify: minify
    };
})();

// Export for Node.js testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JsonFormatter;
}
