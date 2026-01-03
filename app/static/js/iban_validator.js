/**
 * IBAN Validator Library
 * Local IBAN validation using MOD-97 checksum algorithm
 * Works in both browser and Node.js environments
 */

(function(root, factory) {
    if (typeof module === 'object' && module.exports) {
        // Node.js
        module.exports = factory();
    } else {
        // Browser
        root.IbanValidator = factory();
    }
}(typeof self !== 'undefined' ? self : this, function() {
    'use strict';

    // IBAN lengths by country (ISO 3166-1 alpha-2)
    const IBAN_LENGTHS = {
        'AD': 24, 'AE': 23, 'AL': 28, 'AT': 20, 'AZ': 28,
        'BA': 20, 'BE': 16, 'BG': 22, 'BH': 22, 'BR': 29,
        'BY': 28, 'CH': 21, 'CR': 22, 'CY': 28, 'CZ': 24,
        'DE': 22, 'DK': 18, 'DO': 28, 'EE': 20, 'EG': 29,
        'ES': 24, 'FI': 18, 'FO': 18, 'FR': 27, 'GB': 22,
        'GE': 22, 'GI': 23, 'GL': 18, 'GR': 27, 'GT': 28,
        'HR': 21, 'HU': 28, 'IE': 22, 'IL': 23, 'IQ': 23,
        'IS': 26, 'IT': 27, 'JO': 30, 'KW': 30, 'KZ': 20,
        'LB': 28, 'LC': 32, 'LI': 21, 'LT': 20, 'LU': 20,
        'LV': 21, 'MC': 27, 'MD': 24, 'ME': 22, 'MK': 19,
        'MR': 27, 'MT': 31, 'MU': 30, 'NL': 18, 'NO': 15,
        'PK': 24, 'PL': 28, 'PS': 29, 'PT': 25, 'QA': 29,
        'RO': 24, 'RS': 22, 'SA': 24, 'SC': 31, 'SE': 24,
        'SI': 19, 'SK': 24, 'SM': 27, 'ST': 25, 'SV': 28,
        'TL': 23, 'TN': 24, 'TR': 26, 'UA': 29, 'VA': 22,
        'VG': 24, 'XK': 20
    };

    // Country names
    const COUNTRY_NAMES = {
        'AD': 'Andorra', 'AE': 'United Arab Emirates', 'AL': 'Albania',
        'AT': 'Austria', 'AZ': 'Azerbaijan', 'BA': 'Bosnia and Herzegovina',
        'BE': 'Belgium', 'BG': 'Bulgaria', 'BH': 'Bahrain', 'BR': 'Brazil',
        'BY': 'Belarus', 'CH': 'Switzerland', 'CR': 'Costa Rica', 'CY': 'Cyprus',
        'CZ': 'Czech Republic', 'DE': 'Germany', 'DK': 'Denmark',
        'DO': 'Dominican Republic', 'EE': 'Estonia', 'EG': 'Egypt',
        'ES': 'Spain', 'FI': 'Finland', 'FO': 'Faroe Islands', 'FR': 'France',
        'GB': 'United Kingdom', 'GE': 'Georgia', 'GI': 'Gibraltar',
        'GL': 'Greenland', 'GR': 'Greece', 'GT': 'Guatemala', 'HR': 'Croatia',
        'HU': 'Hungary', 'IE': 'Ireland', 'IL': 'Israel', 'IQ': 'Iraq',
        'IS': 'Iceland', 'IT': 'Italy', 'JO': 'Jordan', 'KW': 'Kuwait',
        'KZ': 'Kazakhstan', 'LB': 'Lebanon', 'LC': 'Saint Lucia',
        'LI': 'Liechtenstein', 'LT': 'Lithuania', 'LU': 'Luxembourg',
        'LV': 'Latvia', 'MC': 'Monaco', 'MD': 'Moldova', 'ME': 'Montenegro',
        'MK': 'North Macedonia', 'MR': 'Mauritania', 'MT': 'Malta',
        'MU': 'Mauritius', 'NL': 'Netherlands', 'NO': 'Norway', 'PK': 'Pakistan',
        'PL': 'Poland', 'PS': 'Palestine', 'PT': 'Portugal', 'QA': 'Qatar',
        'RO': 'Romania', 'RS': 'Serbia', 'SA': 'Saudi Arabia', 'SC': 'Seychelles',
        'SE': 'Sweden', 'SI': 'Slovenia', 'SK': 'Slovakia', 'SM': 'San Marino',
        'ST': 'São Tomé and Príncipe', 'SV': 'El Salvador', 'TL': 'East Timor',
        'TN': 'Tunisia', 'TR': 'Turkey', 'UA': 'Ukraine', 'VA': 'Vatican City',
        'VG': 'British Virgin Islands', 'XK': 'Kosovo'
    };

    /**
     * Remove spaces and convert to uppercase
     * @param {string} iban - Raw IBAN input
     * @returns {string} Cleaned IBAN
     */
    function cleanIban(iban) {
        if (!iban || typeof iban !== 'string') {
            return '';
        }
        return iban.replace(/\s/g, '').toUpperCase();
    }

    /**
     * Format IBAN with spaces every 4 characters
     * @param {string} iban - IBAN to format
     * @returns {string} Formatted IBAN
     */
    function formatIban(iban) {
        const cleaned = cleanIban(iban);
        return cleaned.replace(/(.{4})/g, '$1 ').trim();
    }

    /**
     * Extract country code from IBAN
     * @param {string} iban - IBAN
     * @returns {string} Two-letter country code
     */
    function getCountryCode(iban) {
        const cleaned = cleanIban(iban);
        return cleaned.substring(0, 2);
    }

    /**
     * Extract check digits from IBAN
     * @param {string} iban - IBAN
     * @returns {string} Two check digits
     */
    function getCheckDigits(iban) {
        const cleaned = cleanIban(iban);
        return cleaned.substring(2, 4);
    }

    /**
     * Extract BBAN (Basic Bank Account Number) from IBAN
     * @param {string} iban - IBAN
     * @returns {string} BBAN
     */
    function getBban(iban) {
        const cleaned = cleanIban(iban);
        return cleaned.substring(4);
    }

    /**
     * Get country name from country code
     * @param {string} countryCode - Two-letter country code
     * @returns {string|null} Country name or null if unknown
     */
    function getCountryName(countryCode) {
        return COUNTRY_NAMES[countryCode.toUpperCase()] || null;
    }

    /**
     * Get expected IBAN length for a country
     * @param {string} countryCode - Two-letter country code
     * @returns {number|null} Expected length or null if unknown
     */
    function getExpectedLength(countryCode) {
        return IBAN_LENGTHS[countryCode.toUpperCase()] || null;
    }

    /**
     * Check if country code is valid/supported
     * @param {string} countryCode - Two-letter country code
     * @returns {boolean}
     */
    function isValidCountryCode(countryCode) {
        return IBAN_LENGTHS.hasOwnProperty(countryCode.toUpperCase());
    }

    /**
     * Convert letter to number for MOD-97 calculation (A=10, B=11, ..., Z=35)
     * @param {string} char - Single character
     * @returns {string} Number string
     */
    function letterToNumber(char) {
        const code = char.charCodeAt(0);
        if (code >= 65 && code <= 90) { // A-Z
            return (code - 55).toString();
        }
        return char; // Already a digit
    }

    /**
     * Calculate MOD-97 of a large number string
     * @param {string} numStr - Number as string
     * @returns {number} Remainder after dividing by 97
     */
    function mod97(numStr) {
        let remainder = 0;
        for (let i = 0; i < numStr.length; i++) {
            remainder = (remainder * 10 + parseInt(numStr[i], 10)) % 97;
        }
        return remainder;
    }

    /**
     * Validate IBAN checksum using MOD-97 algorithm
     * @param {string} iban - Cleaned IBAN
     * @returns {boolean} True if checksum is valid
     */
    function validateChecksum(iban) {
        const cleaned = cleanIban(iban);
        
        // Move first 4 characters to end
        const rearranged = cleaned.substring(4) + cleaned.substring(0, 4);
        
        // Convert letters to numbers
        let numStr = '';
        for (const char of rearranged) {
            numStr += letterToNumber(char);
        }
        
        // Valid if MOD-97 equals 1
        return mod97(numStr) === 1;
    }

    /**
     * Validate IBAN format (basic structure check)
     * @param {string} iban - IBAN to validate
     * @returns {{valid: boolean, error: string|null}}
     */
    function validateFormat(iban) {
        const cleaned = cleanIban(iban);
        
        if (!cleaned) {
            return { valid: false, error: 'IBAN is empty' };
        }
        
        if (cleaned.length < 5) {
            return { valid: false, error: 'IBAN is too short' };
        }
        
        // Check country code (first 2 chars must be letters)
        const countryCode = cleaned.substring(0, 2);
        if (!/^[A-Z]{2}$/.test(countryCode)) {
            return { valid: false, error: 'Invalid country code format' };
        }
        
        // Check digits (chars 3-4 must be digits)
        const checkDigits = cleaned.substring(2, 4);
        if (!/^\d{2}$/.test(checkDigits)) {
            return { valid: false, error: 'Invalid check digits format' };
        }
        
        // Check BBAN (rest must be alphanumeric)
        const bban = cleaned.substring(4);
        if (!/^[A-Z0-9]+$/.test(bban)) {
            return { valid: false, error: 'Invalid BBAN format (must be alphanumeric)' };
        }
        
        return { valid: true, error: null };
    }

    /**
     * Validate IBAN length for the country
     * @param {string} iban - IBAN to validate
     * @returns {{valid: boolean, error: string|null}}
     */
    function validateLength(iban) {
        const cleaned = cleanIban(iban);
        const countryCode = getCountryCode(cleaned);
        const expectedLength = getExpectedLength(countryCode);
        
        if (expectedLength === null) {
            return { valid: false, error: `Unknown country code: ${countryCode}` };
        }
        
        if (cleaned.length !== expectedLength) {
            return { 
                valid: false, 
                error: `Invalid length for ${countryCode}: expected ${expectedLength}, got ${cleaned.length}` 
            };
        }
        
        return { valid: true, error: null };
    }

    /**
     * Full IBAN validation
     * @param {string} iban - IBAN to validate
     * @returns {{valid: boolean, errors: string[], iban: string, countryCode: string, countryName: string|null, checkDigits: string, bban: string, formatted: string}}
     */
    function validate(iban) {
        const cleaned = cleanIban(iban);
        const errors = [];
        
        const result = {
            valid: false,
            errors: [],
            iban: cleaned,
            countryCode: '',
            countryName: null,
            checkDigits: '',
            bban: '',
            formatted: ''
        };
        
        // Format validation
        const formatResult = validateFormat(cleaned);
        if (!formatResult.valid) {
            result.errors.push(formatResult.error);
            return result;
        }
        
        // Extract parts
        result.countryCode = getCountryCode(cleaned);
        result.countryName = getCountryName(result.countryCode);
        result.checkDigits = getCheckDigits(cleaned);
        result.bban = getBban(cleaned);
        result.formatted = formatIban(cleaned);
        
        // Length validation
        const lengthResult = validateLength(cleaned);
        if (!lengthResult.valid) {
            result.errors.push(lengthResult.error);
            return result;
        }
        
        // Checksum validation
        if (!validateChecksum(cleaned)) {
            result.errors.push('Invalid checksum');
            return result;
        }
        
        result.valid = true;
        return result;
    }

    /**
     * Generate check digits for a given country code and BBAN
     * @param {string} countryCode - Two-letter country code
     * @param {string} bban - Basic Bank Account Number
     * @returns {{checkDigits: string|null, error: string|null}}
     */
    function generateCheckDigits(countryCode, bban) {
        const cc = countryCode.toUpperCase();
        const cleanBban = bban.toUpperCase().replace(/\s/g, '');
        
        if (!isValidCountryCode(cc)) {
            return { checkDigits: null, error: `Unknown country code: ${cc}` };
        }
        
        // Create IBAN with 00 as check digits
        const tempIban = cleanBban + cc + '00';
        
        // Convert to numbers
        let numStr = '';
        for (const char of tempIban) {
            numStr += letterToNumber(char);
        }
        
        // Calculate check digits: 98 - (numStr mod 97)
        const remainder = mod97(numStr);
        const checkDigits = (98 - remainder).toString().padStart(2, '0');
        
        return { checkDigits, error: null };
    }

    // Public API
    return {
        IBAN_LENGTHS: IBAN_LENGTHS,
        COUNTRY_NAMES: COUNTRY_NAMES,
        cleanIban: cleanIban,
        formatIban: formatIban,
        getCountryCode: getCountryCode,
        getCheckDigits: getCheckDigits,
        getBban: getBban,
        getCountryName: getCountryName,
        getExpectedLength: getExpectedLength,
        isValidCountryCode: isValidCountryCode,
        validateFormat: validateFormat,
        validateLength: validateLength,
        validateChecksum: validateChecksum,
        validate: validate,
        generateCheckDigits: generateCheckDigits
    };
}));
