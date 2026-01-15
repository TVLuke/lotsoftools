/**
 * Holiday Calendar Utility Functions
 * Pure functions for date formatting, filtering, and calendar generation
 */

const HolidayCalendar = (function() {
    'use strict';

    const labels = {
        de: {
            all: 'Alle',
            loading: 'Laden...',
            error: 'Fehler beim Laden',
            noEntries: 'Keine Einträge gefunden',
            publicHoliday: 'Feiertag',
            schoolHoliday: 'Ferien'
        },
        en: {
            all: 'All',
            loading: 'Loading...',
            error: 'Error loading data',
            noEntries: 'No entries found',
            publicHoliday: 'Public Holiday',
            schoolHoliday: 'School Holiday'
        },
        fr: {
            all: 'Tous',
            loading: 'Chargement...',
            error: 'Erreur de chargement',
            noEntries: 'Aucune entrée trouvée',
            publicHoliday: 'Jour férié',
            schoolHoliday: 'Vacances'
        },
        es: {
            all: 'Todos',
            loading: 'Cargando...',
            error: 'Error al cargar',
            noEntries: 'No se encontraron entradas',
            publicHoliday: 'Día festivo',
            schoolHoliday: 'Vacaciones'
        },
        it: {
            all: 'Tutti',
            loading: 'Caricamento...',
            error: 'Errore di caricamento',
            noEntries: 'Nessuna voce trovata',
            publicHoliday: 'Giorno festivo',
            schoolHoliday: 'Vacanze'
        }
    };

    const monthNames = {
        'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        'de': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
        'fr': ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
        'es': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        'it': ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
    };

    const dayNamesShort = {
        'en': ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'],
        'de': ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'],
        'fr': ['Lu', 'Ma', 'Me', 'Je', 'Ve', 'Sa', 'Di'],
        'es': ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá', 'Do'],
        'it': ['Lu', 'Ma', 'Me', 'Gi', 'Ve', 'Sa', 'Do']
    };

    /**
     * Get translation object for a language
     * @param {string} lang - Language code (de, en, fr, es, it)
     * @returns {object} Translation object
     */
    function getLabels(lang) {
        const normalizedLang = (lang || 'en').toLowerCase();
        return labels[normalizedLang] || labels.en;
    }

    /**
     * Get locale string for date formatting
     * @param {string} lang - Language code (DE, EN, FR, ES, IT)
     * @returns {string} Locale string
     */
    function getLocale(lang) {
        const upperLang = (lang || 'EN').toUpperCase();
        if (upperLang === 'DE') return 'de-DE';
        if (upperLang === 'FR') return 'fr-FR';
        if (upperLang === 'ES') return 'es-ES';
        if (upperLang === 'IT') return 'it-IT';
        return 'en-GB';
    }

    /**
     * Format a single date string
     * @param {string} dateStr - Date in YYYY-MM-DD format
     * @param {string} locale - Locale string for formatting
     * @returns {string} Formatted date string
     */
    function formatDate(dateStr, locale) {
        if (!dateStr) return '';
        const date = new Date(dateStr + 'T00:00:00');
        return date.toLocaleDateString(locale || 'en-GB', { 
            weekday: 'short',
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric' 
        });
    }

    /**
     * Format a date range
     * @param {string} start - Start date in YYYY-MM-DD format
     * @param {string} end - End date in YYYY-MM-DD format
     * @param {string} locale - Locale string for formatting
     * @returns {string} Formatted date range string
     */
    function formatDateRange(start, end, locale) {
        if (!start) return '';
        if (!end || start === end) {
            return formatDate(start, locale);
        }
        const startDate = new Date(start + 'T00:00:00');
        const endDate = new Date(end + 'T00:00:00');
        const loc = locale || 'en-GB';
        
        const startStr = startDate.toLocaleDateString(loc, { 
            weekday: 'short',
            day: '2-digit', 
            month: '2-digit'
        });
        const endStr = endDate.toLocaleDateString(loc, { 
            weekday: 'short',
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric' 
        });
        
        return `${startStr} – ${endStr}`;
    }

    /**
     * Filter holidays by year
     * @param {Array} holidays - Array of holiday objects
     * @param {string|number} year - Year to filter by, or 'all'
     * @returns {Array} Filtered holidays
     */
    function filterHolidaysByYear(holidays, year) {
        if (year === 'all' || year === null || year === undefined) return holidays;
        const yearInt = parseInt(year);
        if (isNaN(yearInt)) return holidays;
        
        return holidays.filter(h => {
            const startYear = new Date(h.start_date + 'T00:00:00').getFullYear();
            const endYear = h.end_date ? new Date(h.end_date + 'T00:00:00').getFullYear() : startYear;
            return startYear === yearInt || endYear === yearInt;
        });
    }

    /**
     * Create a map of dates to holiday types for calendar rendering
     * @param {Array} holidays - Array of holiday objects
     * @param {number} year - Year to map
     * @returns {object} Map of date strings to {public: bool, school: bool}
     */
    function getHolidayMap(holidays, year) {
        const map = {};
        holidays.forEach(h => {
            const start = new Date(h.start_date + 'T00:00:00');
            const end = h.end_date ? new Date(h.end_date + 'T00:00:00') : start;
            
            for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
                if (d.getFullYear() === year) {
                    const key = d.toISOString().split('T')[0];
                    if (!map[key]) map[key] = { public: false, school: false };
                    if (h.type === 'public') map[key].public = true;
                    else map[key].school = true;
                }
            }
        });
        return map;
    }

    /**
     * Get ISO 8601 week number for a date
     * @param {Date} date - Date object
     * @returns {number} Week number (1-53)
     */
    function getWeekNumber(date) {
        const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
        const dayNum = d.getUTCDay() || 7;
        d.setUTCDate(d.getUTCDate() + 4 - dayNum);
        const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
        return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    }

    /**
     * Get month names for a language
     * @param {string} lang - Language code
     * @returns {Array} Array of month names
     */
    function getMonthNames(lang) {
        const normalizedLang = (lang || 'en').toLowerCase();
        return monthNames[normalizedLang] || monthNames['en'];
    }

    /**
     * Get short day names for a language
     * @param {string} lang - Language code
     * @returns {Array} Array of short day names
     */
    function getDayNamesShort(lang) {
        const normalizedLang = (lang || 'en').toLowerCase();
        return dayNamesShort[normalizedLang] || dayNamesShort['en'];
    }

    // Public API
    return {
        getLabels,
        getLocale,
        formatDate,
        formatDateRange,
        filterHolidaysByYear,
        getHolidayMap,
        getWeekNumber,
        getMonthNames,
        getDayNamesShort
    };
})();

// Export for Node.js testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HolidayCalendar;
}
