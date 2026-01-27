/**
 * Resistor Color Code Calculator Library
 * Based on IEC 60062 international standard
 */

const ResistorCalculator = (function() {
    'use strict';

    const colors = {
        black:  { digit: 0, multiplier: 1 },
        brown:  { digit: 1, multiplier: 10, tolerance: 1, tcr: 100 },
        red:    { digit: 2, multiplier: 100, tolerance: 2, tcr: 50 },
        orange: { digit: 3, multiplier: 1000, tcr: 15 },
        yellow: { digit: 4, multiplier: 10000, tcr: 25 },
        green:  { digit: 5, multiplier: 100000, tolerance: 0.5, tcr: 20 },
        blue:   { digit: 6, multiplier: 1000000, tolerance: 0.25, tcr: 10 },
        violet: { digit: 7, multiplier: 10000000, tolerance: 0.1, tcr: 5 },
        grey:   { digit: 8, multiplier: 100000000, tolerance: 0.05, tcr: 1 },
        white:  { digit: 9, multiplier: 1000000000 },
        gold:   { multiplier: 0.1, tolerance: 5 },
        silver: { multiplier: 0.01, tolerance: 10 },
        none:   { tolerance: 5 }
    };

    /**
     * Calculate resistor value from color bands
     * @param {string[]} bands - Array of color names (3 to 6 bands)
     * @returns {object} - { resistance, tolerance, tcr, min, max, formatted }
     */
    function calculate(bands) {
        if (!bands || bands.length < 3 || bands.length > 6) {
            throw new Error('Invalid number of bands. Must be 3-6 bands.');
        }

        // Normalize color names to lowercase
        bands = bands.map(b => b.toLowerCase().trim());

        // Validate all colors exist
        for (const band of bands) {
            if (!colors[band]) {
                throw new Error(`Unknown color: ${band}`);
            }
        }

        let significantDigits;
        let multiplierBand;
        let toleranceBand;
        let tcrBand;

        if (bands.length === 3) {
            // 3-band: digit, digit, multiplier (20% tolerance assumed)
            significantDigits = colors[bands[0]].digit * 10 + colors[bands[1]].digit;
            multiplierBand = bands[2];
            toleranceBand = 'none';
            tcrBand = null;
        } else if (bands.length === 4) {
            // 4-band: digit, digit, multiplier, tolerance
            significantDigits = colors[bands[0]].digit * 10 + colors[bands[1]].digit;
            multiplierBand = bands[2];
            toleranceBand = bands[3];
            tcrBand = null;
        } else if (bands.length === 5) {
            // 5-band: digit, digit, digit, multiplier, tolerance
            significantDigits = colors[bands[0]].digit * 100 + 
                               colors[bands[1]].digit * 10 + 
                               colors[bands[2]].digit;
            multiplierBand = bands[3];
            toleranceBand = bands[4];
            tcrBand = null;
        } else if (bands.length === 6) {
            // 6-band: digit, digit, digit, multiplier, tolerance, tcr
            significantDigits = colors[bands[0]].digit * 100 + 
                               colors[bands[1]].digit * 10 + 
                               colors[bands[2]].digit;
            multiplierBand = bands[3];
            toleranceBand = bands[4];
            tcrBand = bands[5];
        }

        const multiplier = colors[multiplierBand].multiplier;
        if (multiplier === undefined) {
            throw new Error(`Color ${multiplierBand} cannot be used as multiplier`);
        }

        const resistance = significantDigits * multiplier;

        let tolerance = 20;
        if (colors[toleranceBand] && colors[toleranceBand].tolerance !== undefined) {
            tolerance = colors[toleranceBand].tolerance;
        }

        let tcr = null;
        if (tcrBand && colors[tcrBand] && colors[tcrBand].tcr !== undefined) {
            tcr = colors[tcrBand].tcr;
        }

        const min = resistance * (1 - tolerance / 100);
        const max = resistance * (1 + tolerance / 100);

        return {
            resistance: resistance,
            tolerance: tolerance,
            tcr: tcr,
            min: min,
            max: max,
            formatted: formatResistance(resistance),
            formattedMin: formatResistance(min),
            formattedMax: formatResistance(max)
        };
    }

    /**
     * Format resistance value with appropriate unit
     * @param {number} value - Resistance in ohms
     * @returns {string} - Formatted string with unit
     */
    function formatResistance(value) {
        if (value >= 1000000000) {
            return (value / 1000000000).toFixed(2).replace(/\.?0+$/, '') + ' GΩ';
        } else if (value >= 1000000) {
            return (value / 1000000).toFixed(2).replace(/\.?0+$/, '') + ' MΩ';
        } else if (value >= 1000) {
            return (value / 1000).toFixed(2).replace(/\.?0+$/, '') + ' kΩ';
        } else if (value >= 1) {
            return value.toFixed(2).replace(/\.?0+$/, '') + ' Ω';
        } else {
            return (value * 1000).toFixed(2).replace(/\.?0+$/, '') + ' mΩ';
        }
    }

    /**
     * Get color data
     * @returns {object} - Color definitions
     */
    function getColors() {
        return { ...colors };
    }

    /**
     * Check if a color is valid for a specific band type
     * @param {string} color - Color name
     * @param {string} bandType - 'digit', 'multiplier', 'tolerance', or 'tcr'
     * @returns {boolean}
     */
    function isValidColor(color, bandType) {
        const c = colors[color.toLowerCase()];
        if (!c) return false;

        switch (bandType) {
            case 'digit':
                return c.digit !== undefined;
            case 'multiplier':
                return c.multiplier !== undefined;
            case 'tolerance':
                return c.tolerance !== undefined;
            case 'tcr':
                return c.tcr !== undefined;
            default:
                return false;
        }
    }

    // Public API
    return {
        calculate: calculate,
        formatResistance: formatResistance,
        getColors: getColors,
        isValidColor: isValidColor
    };
})();

// Export for Node.js/testing environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ResistorCalculator;
}
