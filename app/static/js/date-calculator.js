/**
 * Date Calculator Utility Functions
 * Extracted from date_calculator.html - calculates difference between two dates
 */

const DateCalculator = (function() {
    'use strict';

    /**
     * Format a number with thousands separators (dots)
     * @param {number} num - Number to format
     * @returns {string} Formatted number
     */
    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }

    /**
     * Calculate the difference between two dates
     * @param {Date} date1 - First date
     * @param {Date} date2 - Second date
     * @returns {Object} Object containing all calculated values
     */
    function calculateDifference(date1, date2) {
        let diffMs = date1 - date2;
        
        // Handle negative values (past/future depending on mode)
        const isNegative = diffMs < 0;
        diffMs = Math.abs(diffMs);
        
        const totalSeconds = Math.floor(diffMs / 1000);
        const totalMinutes = Math.floor(diffMs / (1000 * 60));
        const totalHours = Math.floor(diffMs / (1000 * 60 * 60));
        const totalDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        // Years decimal (approximate: 365.25 days per year)
        const yearsDecimalVal = (diffMs / (1000 * 60 * 60 * 24 * 365.25)).toFixed(6);
        
        // Full format: years, months, days, hours, minutes, seconds
        const years = Math.floor(totalDays / 365.25);
        const remainingDaysAfterYears = totalDays - Math.floor(years * 365.25);
        const months = Math.floor(remainingDaysAfterYears / 30.44);
        const days = Math.floor(remainingDaysAfterYears - Math.floor(months * 30.44));
        const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diffMs % (1000 * 60)) / 1000);
        
        // Days format
        const daysHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const daysMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
        const daysSeconds = Math.floor((diffMs % (1000 * 60)) / 1000);
        
        // Hours format
        const hoursMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
        const hoursSeconds = Math.floor((diffMs % (1000 * 60)) / 1000);
        
        // Minutes format
        const minutesSeconds = Math.floor((diffMs % (1000 * 60)) / 1000);
        
        const prefix = isNegative ? '-' : '';
        
        return {
            isNegative,
            prefix,
            diffMs,
            totalSeconds,
            totalMinutes,
            totalHours,
            totalDays,
            yearsDecimalVal,
            years,
            months,
            days,
            hours,
            minutes,
            seconds,
            daysHours,
            daysMinutes,
            daysSeconds,
            hoursMinutes,
            hoursSeconds,
            minutesSeconds
        };
    }

    /**
     * Format the difference as a full string (years, months, days, hours, minutes, seconds)
     * @param {Object} diff - Result from calculateDifference
     * @returns {string} Formatted string
     */
    function formatFull(diff) {
        return `${diff.prefix}${diff.years}y ${diff.months}m ${diff.days}d ${diff.hours.toString().padStart(2, '0')}:${diff.minutes.toString().padStart(2, '0')}:${diff.seconds.toString().padStart(2, '0')}`;
    }

    /**
     * Format the difference as years decimal
     * @param {Object} diff - Result from calculateDifference
     * @returns {string} Formatted string
     */
    function formatYearsDecimal(diff) {
        return `${diff.prefix}${diff.yearsDecimalVal}`;
    }

    /**
     * Format the difference as days, hours, minutes, seconds
     * @param {Object} diff - Result from calculateDifference
     * @returns {string} Formatted string
     */
    function formatDays(diff) {
        return `${diff.prefix}${formatNumber(diff.totalDays)}d ${diff.daysHours.toString().padStart(2, '0')}:${diff.daysMinutes.toString().padStart(2, '0')}:${diff.daysSeconds.toString().padStart(2, '0')}`;
    }

    /**
     * Format the difference as hours, minutes, seconds
     * @param {Object} diff - Result from calculateDifference
     * @returns {string} Formatted string
     */
    function formatHours(diff) {
        return `${diff.prefix}${formatNumber(diff.totalHours)}:${diff.hoursMinutes.toString().padStart(2, '0')}:${diff.hoursSeconds.toString().padStart(2, '0')}`;
    }

    /**
     * Format the difference as minutes, seconds
     * @param {Object} diff - Result from calculateDifference
     * @returns {string} Formatted string
     */
    function formatMinutes(diff) {
        return `${diff.prefix}${formatNumber(diff.totalMinutes)}:${diff.minutesSeconds.toString().padStart(2, '0')}`;
    }

    /**
     * Format the difference as total seconds
     * @param {Object} diff - Result from calculateDifference
     * @returns {string} Formatted string
     */
    function formatSeconds(diff) {
        return `${diff.prefix}${formatNumber(diff.totalSeconds)}`;
    }

    /**
     * Format the difference as months and days only
     * @param {Object} diff - Result from calculateDifference
     * @param {string} lang - Language code ('en' or 'de')
     * @returns {string} Formatted string
     */
    function formatMonthsDays(diff, lang) {
        const totalMonths = diff.years * 12 + diff.months;
        if (lang === 'de') {
            return `${diff.prefix}${totalMonths} Monat${totalMonths !== 1 ? 'e' : ''}, ${diff.days} Tag${diff.days !== 1 ? 'e' : ''}`;
        }
        return `${diff.prefix}${totalMonths} month${totalMonths !== 1 ? 's' : ''}, ${diff.days} day${diff.days !== 1 ? 's' : ''}`;
    }

    /**
     * Format the difference as total days only
     * @param {Object} diff - Result from calculateDifference
     * @param {string} lang - Language code ('en' or 'de')
     * @returns {string} Formatted string
     */
    function formatTotalDays(diff, lang) {
        if (lang === 'de') {
            return `${diff.prefix}${formatNumber(diff.totalDays)} Tag${diff.totalDays !== 1 ? 'e' : ''}`;
        }
        return `${diff.prefix}${formatNumber(diff.totalDays)} day${diff.totalDays !== 1 ? 's' : ''}`;
    }

    /**
     * Format the difference as weeks and days
     * @param {Object} diff - Result from calculateDifference
     * @param {string} lang - Language code ('en' or 'de')
     * @returns {string} Formatted string
     */
    function formatWeeksDays(diff, lang) {
        const weeks = Math.floor(diff.totalDays / 7);
        const remainingDays = diff.totalDays % 7;
        if (lang === 'de') {
            return `${diff.prefix}${formatNumber(weeks)} Woche${weeks !== 1 ? 'n' : ''}, ${remainingDays} Tag${remainingDays !== 1 ? 'e' : ''}`;
        }
        return `${diff.prefix}${formatNumber(weeks)} week${weeks !== 1 ? 's' : ''}, ${remainingDays} day${remainingDays !== 1 ? 's' : ''}`;
    }

    /**
     * Get all formatted outputs at once
     * @param {Date} date1 - First date
     * @param {Date} date2 - Second date
     * @param {string} lang - Language code ('en' or 'de')
     * @returns {Object} Object with all formatted strings
     */
    function getAllFormats(date1, date2, lang) {
        lang = lang || 'en';
        const diff = calculateDifference(date1, date2);
        return {
            full: formatFull(diff),
            yearsDecimal: formatYearsDecimal(diff),
            days: formatDays(diff),
            hours: formatHours(diff),
            minutes: formatMinutes(diff),
            seconds: formatSeconds(diff),
            monthsDays: formatMonthsDays(diff, lang),
            totalDays: formatTotalDays(diff, lang),
            weeksDays: formatWeeksDays(diff, lang),
            raw: diff
        };
    }

    return {
        formatNumber,
        calculateDifference,
        formatFull,
        formatYearsDecimal,
        formatDays,
        formatHours,
        formatMinutes,
        formatSeconds,
        formatMonthsDays,
        formatTotalDays,
        formatWeeksDays,
        getAllFormats
    };
})();

// Export for Node.js testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DateCalculator;
}
