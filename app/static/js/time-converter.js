/**
 * Time Converter Library
 * Provides functions to parse and format dates in various formats.
 * Uses native JavaScript Date and Intl.DateTimeFormat APIs.
 */

const TimeConverter = (function() {
    'use strict';

    // Allowed strftime directives (whitelist for security)
    const ALLOWED_DIRECTIVES = new Set([
        '%Y', '%y', '%m', '%d', '%H', '%I', '%M', '%S', '%p', '%P',
        '%z', '%Z', '%A', '%a', '%B', '%b', '%j', '%W', '%U', '%w',
        '%e', '%k', '%l', '%s', '%n', '%t', '%%',
        '%C', '%G', '%g', '%V', '%u', '%F', '%T', '%R', '%r', '%D', '%x', '%X', '%c'
    ]);

    // Cached Intl.DateTimeFormat instances for performance
    const formatters = {
        weekdayLong: new Intl.DateTimeFormat('en-US', { weekday: 'long' }),
        weekdayShort: new Intl.DateTimeFormat('en-US', { weekday: 'short' }),
        monthLong: new Intl.DateTimeFormat('en-US', { month: 'long' }),
        monthShort: new Intl.DateTimeFormat('en-US', { month: 'short' }),
        timezoneName: new Intl.DateTimeFormat('en-US', { timeZoneName: 'short' })
    };

    /**
     * Pad a number with leading zeros
     * @param {number} n - Number to pad
     * @param {number} len - Desired length
     * @returns {string}
     */
    function pad(n, len) {
        len = len || 2;
        return String(n).padStart(len, '0');
    }

    /**
     * Validate a strftime format string for security
     * Only allows known safe directives
     * @param {string} format - Format string to validate
     * @returns {boolean}
     */
    function validateFormatString(format) {
        if (!format || typeof format !== 'string') return false;
        if (format.length > 100) return false;
        
        const matches = format.match(/%./g) || [];
        for (const match of matches) {
            if (!ALLOWED_DIRECTIVES.has(match)) {
                return false;
            }
        }
        return true;
    }

    /**
     * Get day of year (1-366)
     * @param {Date} date
     * @returns {number}
     */
    function getDayOfYear(date) {
        const start = new Date(date.getFullYear(), 0, 0);
        const diff = date - start;
        return Math.floor(diff / (1000 * 60 * 60 * 24));
    }

    /**
     * Get ISO week number using Intl (where supported) or calculation
     * @param {Date} date
     * @returns {number}
     */
    function getISOWeekNumber(date) {
        // Calculate ISO week number
        const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
        d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
        const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
        return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    }

    /**
     * Get week number (Monday as first day of week)
     * @param {Date} date
     * @returns {number}
     */
    function getWeekNumber(date) {
        return getISOWeekNumber(date);
    }

    /**
     * Get week number (Sunday as first day of week)
     * @param {Date} date
     * @returns {number}
     */
    function getWeekNumberSunday(date) {
        const d = new Date(date.getFullYear(), date.getMonth(), date.getDate());
        d.setDate(d.getDate() - d.getDay());
        const yearStart = new Date(d.getFullYear(), 0, 1);
        return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    }

    /**
     * Get ISO week year
     * @param {Date} date
     * @returns {number}
     */
    function getISOWeekYear(date) {
        const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
        d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
        return d.getUTCFullYear();
    }

    /**
     * Get timezone offset string (+0000 format) using native getTimezoneOffset
     * @param {Date} date
     * @returns {string}
     */
    function getTimezoneOffset(date) {
        const offset = -date.getTimezoneOffset();
        const sign = offset >= 0 ? '+' : '-';
        const hours = pad(Math.floor(Math.abs(offset) / 60));
        const mins = pad(Math.abs(offset) % 60);
        return sign + hours + mins;
    }

    /**
     * Get timezone name abbreviation using Intl.DateTimeFormat
     * @param {Date} date
     * @returns {string}
     */
    function getTimezoneName(date) {
        try {
            const parts = formatters.timezoneName.formatToParts(date);
            const tzPart = parts.find(function(p) { return p.type === 'timeZoneName'; });
            return tzPart ? tzPart.value : 'UTC';
        } catch (e) {
            return 'UTC';
        }
    }

    /**
     * Format a date using strftime-like pattern
     * Uses Intl.DateTimeFormat for weekday/month names, native methods for the rest
     * @param {Date} date - Date object to format
     * @param {string} format - strftime format string
     * @returns {string|null} Formatted string or null if invalid format
     */
    function strftime(date, format) {
        if (!validateFormatString(format)) {
            return null;
        }

        if (!(date instanceof Date) || isNaN(date.getTime())) {
            return null;
        }

        // Use Intl.DateTimeFormat for locale-aware parts
        const replacements = {
            '%Y': date.getFullYear(),
            '%y': pad(date.getFullYear() % 100),
            '%C': Math.floor(date.getFullYear() / 100),
            '%m': pad(date.getMonth() + 1),
            '%d': pad(date.getDate()),
            '%e': date.getDate(),
            '%H': pad(date.getHours()),
            '%k': date.getHours(),
            '%I': pad(date.getHours() % 12 || 12),
            '%l': date.getHours() % 12 || 12,
            '%M': pad(date.getMinutes()),
            '%S': pad(date.getSeconds()),
            '%p': date.getHours() < 12 ? 'AM' : 'PM',
            '%P': date.getHours() < 12 ? 'am' : 'pm',
            '%A': formatters.weekdayLong.format(date),  // Native Intl
            '%a': formatters.weekdayShort.format(date), // Native Intl
            '%w': date.getDay(),
            '%u': date.getDay() || 7,
            '%B': formatters.monthLong.format(date),    // Native Intl
            '%b': formatters.monthShort.format(date),   // Native Intl
            '%j': pad(getDayOfYear(date), 3),
            '%W': pad(getWeekNumber(date)),
            '%U': pad(getWeekNumberSunday(date)),
            '%V': pad(getISOWeekNumber(date)),
            '%G': getISOWeekYear(date),
            '%g': pad(getISOWeekYear(date) % 100),
            '%s': Math.floor(date.getTime() / 1000),
            '%z': getTimezoneOffset(date),
            '%Z': getTimezoneName(date),
            '%n': '\n',
            '%t': '\t',
            '%%': '%',
            '%F': date.getFullYear() + '-' + pad(date.getMonth() + 1) + '-' + pad(date.getDate()),
            '%T': pad(date.getHours()) + ':' + pad(date.getMinutes()) + ':' + pad(date.getSeconds()),
            '%R': pad(date.getHours()) + ':' + pad(date.getMinutes()),
            '%r': pad(date.getHours() % 12 || 12) + ':' + pad(date.getMinutes()) + ':' + pad(date.getSeconds()) + ' ' + (date.getHours() < 12 ? 'AM' : 'PM'),
            '%D': pad(date.getMonth() + 1) + '/' + pad(date.getDate()) + '/' + pad(date.getFullYear() % 100),
            '%x': date.toLocaleDateString(),  // Native
            '%X': date.toLocaleTimeString(),  // Native
            '%c': date.toLocaleString()       // Native
        };

        var result = format;
        for (var key in replacements) {
            if (replacements.hasOwnProperty(key)) {
                result = result.split(key).join(String(replacements[key]));
            }
        }
        return result;
    }

    /**
     * Parse various date/time input formats
     * @param {string} input - Input string to parse
     * @returns {Date|null} Parsed Date object or null if invalid
     */
    function parse(input) {
        if (!input || typeof input !== 'string') return null;
        input = input.trim();
        if (!input) return null;

        // Unix timestamp in seconds (10-digit number)
        if (/^\d{10}$/.test(input)) {
            return new Date(parseInt(input, 10) * 1000);
        }

        // Unix timestamp in milliseconds (13-digit number)
        if (/^\d{13}$/.test(input)) {
            return new Date(parseInt(input, 10));
        }

        // General numeric input - try as seconds if reasonable
        if (/^\d+$/.test(input)) {
            var num = parseInt(input, 10);
            if (num < 1e11) {
                return new Date(num * 1000);
            } else {
                return new Date(num);
            }
        }

        // Try native Date parsing (handles ISO 8601, RFC 2822, etc.)
        var parsed = new Date(input);
        if (!isNaN(parsed.getTime())) {
            return parsed;
        }

        // Try MM/DD/YYYY or MM/DD/YYYY @ HH:MM format
        var usFormat = input.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})(?:\s*@?\s*(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(am|pm)?)?/i);
        if (usFormat) {
            var m = parseInt(usFormat[1], 10);
            var d = parseInt(usFormat[2], 10);
            var y = parseInt(usFormat[3], 10);
            var h = parseInt(usFormat[4] || 0, 10);
            var min = parseInt(usFormat[5] || 0, 10);
            var s = parseInt(usFormat[6] || 0, 10);
            var ampm = usFormat[7];
            
            if (ampm && ampm.toLowerCase() === 'pm' && h < 12) h += 12;
            if (ampm && ampm.toLowerCase() === 'am' && h === 12) h = 0;
            
            return new Date(y, m - 1, d, h, min, s);
        }

        return null;
    }

    /**
     * Convert Date to Unix timestamp in seconds
     * @param {Date} date
     * @returns {number}
     */
    function toUnixSeconds(date) {
        return Math.floor(date.getTime() / 1000);
    }

    /**
     * Convert Date to Unix timestamp in milliseconds
     * @param {Date} date
     * @returns {number}
     */
    function toUnixMillis(date) {
        return date.getTime();
    }

    /**
     * Convert Date to ISO 8601 string
     * Uses native Date.toISOString()
     * @param {Date} date
     * @returns {string}
     */
    function toISO8601(date) {
        return date.toISOString();
    }

    /**
     * Convert Date to RFC 3339 string
     * Same as ISO 8601 for most purposes
     * @param {Date} date
     * @returns {string}
     */
    function toRFC3339(date) {
        return date.toISOString();
    }

    /**
     * Convert Date to RFC 2822 string
     * Uses native Date.toUTCString() with format adjustment
     * @param {Date} date
     * @returns {string}
     */
    function toRFC2822(date) {
        return date.toUTCString().replace('GMT', '+0000');
    }

    /**
     * Convert Date to UTC string
     * Uses native Date.toUTCString()
     * @param {Date} date
     * @returns {string}
     */
    function toUTCString(date) {
        return date.toUTCString();
    }

    /**
     * Convert Date to local string
     * Uses native Date.toLocaleString()
     * @param {Date} date
     * @returns {string}
     */
    function toLocalString(date) {
        return date.toLocaleString();
    }

    /**
     * Format date to a specific named format
     * @param {Date} date - Date to format
     * @param {string} formatName - Name of format or strftime pattern
     * @returns {string|null}
     */
    function format(date, formatName) {
        if (!(date instanceof Date) || isNaN(date.getTime())) {
            return null;
        }

        switch (formatName) {
            case 'unix_seconds':
                return String(toUnixSeconds(date));
            case 'unix_millis':
                return String(toUnixMillis(date));
            case 'iso8601':
                return toISO8601(date);
            case 'rfc3339':
                return toRFC3339(date);
            case 'rfc2822':
                return toRFC2822(date);
            case 'utc':
                return toUTCString(date);
            case 'local':
                return toLocalString(date);
            default:
                return strftime(date, formatName);
        }
    }

    /**
     * Get all standard formats for a date
     * @param {Date} date
     * @returns {Object} Object with format names as keys and formatted strings as values
     */
    function getAllFormats(date) {
        if (!(date instanceof Date) || isNaN(date.getTime())) {
            return null;
        }

        return {
            unix_seconds: String(toUnixSeconds(date)),
            unix_millis: String(toUnixMillis(date)),
            iso8601: toISO8601(date),
            rfc3339: toRFC3339(date),
            rfc2822: toRFC2822(date),
            utc: toUTCString(date),
            local: toLocalString(date),
            date_only: strftime(date, '%Y-%m-%d'),
            time_only: strftime(date, '%H:%M:%S'),
            us_format: strftime(date, '%m/%d/%Y @ %I:%M%p')
        };
    }

    // Public API
    return {
        parse: parse,
        format: format,
        strftime: strftime,
        validateFormatString: validateFormatString,
        toUnixSeconds: toUnixSeconds,
        toUnixMillis: toUnixMillis,
        toISO8601: toISO8601,
        toRFC3339: toRFC3339,
        toRFC2822: toRFC2822,
        toUTCString: toUTCString,
        toLocalString: toLocalString,
        getAllFormats: getAllFormats,
        getDayOfYear: getDayOfYear,
        getISOWeekNumber: getISOWeekNumber,
        getWeekNumber: getWeekNumber,
        getTimezoneOffset: getTimezoneOffset,
        getTimezoneName: getTimezoneName,
        ALLOWED_DIRECTIVES: ALLOWED_DIRECTIVES
    };
})();

// Export for Node.js testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TimeConverter;
}
