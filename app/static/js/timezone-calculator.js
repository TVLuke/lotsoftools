/**
 * Timezone Calculator Library
 * Provides functions to convert times between timezones with automatic DST handling.
 * Uses native JavaScript Intl.DateTimeFormat API.
 */

const TimezoneCalculator = (function() {
    'use strict';

    /**
     * Get all available IANA timezones
     * @returns {string[]} Array of timezone identifiers
     */
    function getTimezones() {
        return Intl.supportedValuesOf('timeZone');
    }

    /**
     * Get the user's local timezone
     * @returns {string} IANA timezone identifier
     */
    function getLocalTimezone() {
        return Intl.DateTimeFormat().resolvedOptions().timeZone;
    }

    /**
     * Parse time input in various formats
     * Supports: ISO dates, Unix timestamps, time-only (HH:MM, 12-hour AM/PM)
     * @param {string} input - Time string to parse
     * @returns {Date|null} Parsed date or null if invalid
     */
    function parseTimeInput(input) {
        if (!input || typeof input !== 'string') return null;
        
        const trimmed = input.trim();
        let date;
        
        // Try parsing as ISO string (e.g., "2026-05-09T14:30:00")
        if (trimmed.match(/^\d{4}-\d{2}-\d{2}/)) {
            date = new Date(trimmed);
        }
        // Try parsing as Unix timestamp (seconds or milliseconds)
        else if (/^\d+$/.test(trimmed)) {
            const num = parseInt(trimmed);
            // If > 10 billion, assume milliseconds; otherwise seconds
            date = new Date(num > 10000000000 ? num : num * 1000);
        }
        // Try parsing time only (HH:MM, HH:MM:SS, HH:MM:SS.mmm, or H:MM AM/PM)
        else if (trimmed.match(/^\d{1,2}:\d{2}/)) {
            const now = new Date();
            const timeStr = trimmed.toLowerCase();
            let hours, minutes, seconds = 0, milliseconds = 0;
            
            // Handle AM/PM format
            if (timeStr.includes('am') || timeStr.includes('pm')) {
                const isPM = timeStr.includes('pm');
                const timePart = timeStr.replace(/[ap]m/g, '').trim();
                const parts = timePart.split(':');
                hours = parseInt(parts[0]);
                minutes = parseInt(parts[1]);
                if (parts[2]) {
                    const secParts = parts[2].split('.');
                    seconds = parseInt(secParts[0]);
                    if (secParts[1]) milliseconds = parseInt(secParts[1].padEnd(3, '0').slice(0, 3));
                }
                if (isPM && hours !== 12) hours += 12;
                if (!isPM && hours === 12) hours = 0;
            } else {
                const parts = trimmed.split(':');
                hours = parseInt(parts[0]);
                minutes = parseInt(parts[1]);
                if (parts[2]) {
                    const secParts = parts[2].split('.');
                    seconds = parseInt(secParts[0]);
                    if (secParts[1]) milliseconds = parseInt(secParts[1].padEnd(3, '0').slice(0, 3));
                }
            }
            
            // Use today's date with specified time
            date = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hours, minutes, seconds, milliseconds);
        }
        // Try native Date parsing as fallback
        else {
            date = new Date(trimmed);
        }
        
        // Validate
        if (isNaN(date.getTime())) {
            return null;
        }
        
        return date;
    }

    /**
     * Format a date in a specific timezone
     * @param {Date} date - Date to format
     * @param {string} timezone - IANA timezone identifier
     * @param {Object} options - Intl.DateTimeFormat options
     * @returns {string} Formatted date string
     */
    function formatInTimezone(date, timezone, options = {}) {
        const defaultOptions = {
            timeZone: timezone,
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        };
        
        const formatter = new Intl.DateTimeFormat('en-US', {
            ...defaultOptions,
            ...options
        });
        
        return formatter.format(date);
    }

    /**
     * Get timezone offset string (e.g., "+01:00" or "-05:00")
     * Automatically handles DST based on the date
     * @param {Date} date - Date to get offset for
     * @param {string} timezone - IANA timezone identifier
     * @returns {string} Offset string like "+01:00"
     */
    function getTimezoneOffset(date, timezone) {
        try {
            // Try using longOffset format (newer browsers)
            const formatter = new Intl.DateTimeFormat('en-US', {
                timeZone: timezone,
                timeZoneName: 'longOffset'
            });
            
            const parts = formatter.formatToParts(date);
            const offsetPart = parts.find(p => p.type === 'timeZoneName');
            
            if (offsetPart && offsetPart.value.startsWith('GMT')) {
                return offsetPart.value.replace('GMT', '');
            }
        } catch (e) {
            // Fallback for older browsers
        }
        
        // Fallback: calculate offset manually
        const utcDate = new Date(date.toLocaleString('en-US', { timeZone: 'UTC' }));
        const tzDate = new Date(date.toLocaleString('en-US', { timeZone: timezone }));
        const diff = (tzDate - utcDate) / (1000 * 60); // difference in minutes
        
        const hours = Math.floor(Math.abs(diff) / 60);
        const minutes = Math.abs(diff) % 60;
        const sign = diff >= 0 ? '+' : '-';
        
        return `${sign}${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
    }

    /**
     * Convert a time from one timezone to another
     * @param {Date} date - Date to convert
     * @param {string} sourceTimezone - Source IANA timezone
     * @param {string} targetTimezone - Target IANA timezone
     * @returns {Object} Conversion result with formatted times and offsets
     */
    function convert(date, sourceTimezone, targetTimezone) {
        if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
            throw new Error('Invalid date');
        }
        
        if (!sourceTimezone || !targetTimezone) {
            throw new Error('Source and target timezones are required');
        }
        
        const sourceFormatted = formatInTimezone(date, sourceTimezone, { timeZoneName: 'long' });
        const targetFormatted = formatInTimezone(date, targetTimezone, { timeZoneName: 'long' });
        
        const sourceOffset = getTimezoneOffset(date, sourceTimezone);
        const targetOffset = getTimezoneOffset(date, targetTimezone);
        
        return {
            source: {
                timezone: sourceTimezone,
                formatted: sourceFormatted,
                offset: sourceOffset
            },
            target: {
                timezone: targetTimezone,
                formatted: targetFormatted,
                offset: targetOffset
            },
            date: date
        };
    }

    /**
     * Check if a timezone is valid
     * @param {string} timezone - Timezone to validate
     * @returns {boolean} True if valid
     */
    function isValidTimezone(timezone) {
        try {
            Intl.DateTimeFormat(undefined, { timeZone: timezone });
            return true;
        } catch (e) {
            return false;
        }
    }

    // Public API
    return {
        getTimezones,
        getLocalTimezone,
        parseTimeInput,
        formatInTimezone,
        getTimezoneOffset,
        convert,
        isValidTimezone
    };
})();

// Export for Node.js testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TimezoneCalculator;
}
