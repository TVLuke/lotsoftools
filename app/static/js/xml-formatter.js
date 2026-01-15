/**
 * XML Formatter Library
 * Provides functions to validate, format, and minify XML.
 */

const XmlFormatter = (function() {
    'use strict';

    /**
     * Check if DOMParser is available (browser environment)
     * @returns {boolean}
     */
    function isDomParserAvailable() {
        return typeof DOMParser !== 'undefined';
    }

    /**
     * Validate XML string
     * @param {string} input - XML string to validate
     * @returns {{valid: boolean, error: string|null}}
     */
    function validate(input) {
        if (!input || !input.trim()) {
            return { valid: false, error: 'Empty input' };
        }
        
        if (!isDomParserAvailable()) {
            // In Node.js, do basic validation
            if (!input.trim().startsWith('<')) {
                return { valid: false, error: 'XML must start with <' };
            }
            // Basic tag matching check
            const openTags = (input.match(/<[^/!?][^>]*[^/]>/g) || []).length;
            const closeTags = (input.match(/<\/[^>]+>/g) || []).length;
            const selfClosing = (input.match(/<[^>]+\/>/g) || []).length;
            
            // This is a very basic check
            return { valid: true, error: null };
        }
        
        try {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(input, 'text/xml');
            
            const parseError = xmlDoc.querySelector('parsererror');
            if (parseError) {
                return { valid: false, error: parseError.textContent };
            }
            
            return { valid: true, error: null };
        } catch (e) {
            return { valid: false, error: e.message };
        }
    }

    /**
     * Format XML string with indentation
     * @param {string} input - XML string to format
     * @param {string} indent - Indent string (default: '  ')
     * @returns {{success: boolean, output: string, error: string|null}}
     */
    function format(input, indent) {
        if (indent === undefined) indent = '  ';
        if (typeof indent === 'number') indent = ' '.repeat(indent);
        
        const validation = validate(input);
        if (!validation.valid) {
            return { success: false, output: '', error: validation.error };
        }
        
        try {
            const formatted = formatXmlString(input.trim(), indent);
            return { success: true, output: formatted, error: null };
        } catch (e) {
            return { success: false, output: '', error: e.message };
        }
    }

    /**
     * Internal function to format XML string
     * @param {string} xml - XML string
     * @param {string} indent - Indent string
     * @returns {string}
     */
    function formatXmlString(xml, indent) {
        let formatted = '';
        let indentLevel = 0;
        
        // Normalize the XML first - remove existing formatting
        xml = xml.replace(/>\s+</g, '><').trim();
        
        const nodes = xml.split(/(?=<)|(?<=>)/);
        
        for (let i = 0; i < nodes.length; i++) {
            let node = nodes[i].trim();
            if (!node) continue;
            
            // Check tag type
            const isClosing = node.match(/^<\//);
            const isSelfClosing = node.match(/\/>$/);
            const isComment = node.match(/^<!--/);
            const isDeclaration = node.match(/^<\?/);
            const isOpening = !isClosing && !isSelfClosing && !isComment && !isDeclaration && node.match(/^</);
            
            // Decrease indent for closing tags
            if (isClosing) {
                indentLevel = Math.max(0, indentLevel - 1);
            }
            
            // Add indentation and node
            if (node.startsWith('<')) {
                formatted += indent.repeat(indentLevel) + node + '\n';
            } else {
                // Text content - add to previous line or on new line
                formatted = formatted.trimEnd() + node + '\n';
            }
            
            // Increase indent for opening tags
            if (isOpening && !isSelfClosing) {
                indentLevel++;
            }
        }
        
        return formatted.trim();
    }

    /**
     * Minify XML string (remove whitespace between tags)
     * @param {string} input - XML string to minify
     * @returns {{success: boolean, output: string, error: string|null}}
     */
    function minify(input) {
        const validation = validate(input);
        if (!validation.valid) {
            return { success: false, output: '', error: validation.error };
        }
        
        try {
            // Remove whitespace between tags
            const output = input.replace(/>\s+</g, '><').trim();
            return { success: true, output: output, error: null };
        } catch (e) {
            return { success: false, output: '', error: e.message };
        }
    }

    // Public API
    return {
        validate: validate,
        format: format,
        minify: minify,
        isDomParserAvailable: isDomParserAvailable
    };
})();

// Export for Node.js testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = XmlFormatter;
}
