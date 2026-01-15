/**
 * YAML Formatter Library
 * Provides functions to validate and format YAML.
 * Note: Requires js-yaml library for full functionality.
 */

const YamlFormatter = (function() {
    'use strict';

    /**
     * Check if js-yaml is available
     * @returns {boolean}
     */
    function isJsYamlAvailable() {
        return typeof jsyaml !== 'undefined';
    }

    /**
     * Validate YAML string
     * @param {string} input - YAML string to validate
     * @returns {{valid: boolean, data: any, error: string|null}}
     */
    function validate(input) {
        if (!input || !input.trim()) {
            return { valid: false, data: null, error: 'Empty input' };
        }
        
        if (!isJsYamlAvailable()) {
            return { valid: false, data: null, error: 'js-yaml library not loaded' };
        }
        
        try {
            const data = jsyaml.load(input);
            return { valid: true, data: data, error: null };
        } catch (e) {
            return { valid: false, data: null, error: e.message };
        }
    }

    /**
     * Format YAML string with indentation
     * @param {string} input - YAML string to format
     * @param {number} indent - Number of spaces for indentation (default: 2)
     * @returns {{success: boolean, output: string, error: string|null}}
     */
    function format(input, indent) {
        if (indent === undefined) indent = 2;
        
        const validation = validate(input);
        if (!validation.valid) {
            return { success: false, output: '', error: validation.error };
        }
        
        try {
            const output = jsyaml.dump(validation.data, {
                indent: indent,
                lineWidth: -1,
                noRefs: true
            });
            return { success: true, output: output, error: null };
        } catch (e) {
            return { success: false, output: '', error: e.message };
        }
    }

    // Public API
    return {
        validate: validate,
        format: format,
        isJsYamlAvailable: isJsYamlAvailable
    };
})();

// Export for Node.js testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = YamlFormatter;
}
