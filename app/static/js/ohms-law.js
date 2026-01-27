/**
 * Ohm's Law Calculator Library
 * Formulas: V = I × R, P = V × I, P = I²R, P = V²/R
 */

const OhmsLaw = (function() {
    'use strict';

    /**
     * Calculate missing values from any two known values
     * @param {object} known - Object with known values { voltage, current, resistance, power }
     * @returns {object} - All four values { voltage, current, resistance, power }
     */
    function calculate(known) {
        let V = known.voltage;
        let I = known.current;
        let R = known.resistance;
        let P = known.power;

        // Count how many values we have
        const knownCount = [V, I, R, P].filter(v => v !== undefined && v !== null && v !== '').length;
        
        if (knownCount < 2) {
            throw new Error('At least two values are required');
        }

        // Convert to numbers
        if (V !== undefined && V !== null && V !== '') V = parseFloat(V);
        if (I !== undefined && I !== null && I !== '') I = parseFloat(I);
        if (R !== undefined && R !== null && R !== '') R = parseFloat(R);
        if (P !== undefined && P !== null && P !== '') P = parseFloat(P);

        // Validate non-negative values
        if ((V !== undefined && V < 0) || (I !== undefined && I < 0) || 
            (R !== undefined && R < 0) || (P !== undefined && P < 0)) {
            throw new Error('Values must be non-negative');
        }

        // Calculate based on which values are known
        // V and I known
        if (isValid(V) && isValid(I)) {
            if (I === 0) {
                R = Infinity;
                P = 0;
            } else {
                R = V / I;
                P = V * I;
            }
        }
        // V and R known
        else if (isValid(V) && isValid(R)) {
            if (R === 0) {
                I = Infinity;
                P = Infinity;
            } else {
                I = V / R;
                P = (V * V) / R;
            }
        }
        // V and P known
        else if (isValid(V) && isValid(P)) {
            if (V === 0) {
                I = P === 0 ? 0 : Infinity;
                R = 0;
            } else {
                I = P / V;
                R = (V * V) / P;
            }
        }
        // I and R known
        else if (isValid(I) && isValid(R)) {
            V = I * R;
            P = I * I * R;
        }
        // I and P known
        else if (isValid(I) && isValid(P)) {
            if (I === 0) {
                V = P === 0 ? 0 : Infinity;
                R = Infinity;
            } else {
                V = P / I;
                R = P / (I * I);
            }
        }
        // R and P known
        else if (isValid(R) && isValid(P)) {
            if (R === 0) {
                V = 0;
                I = P === 0 ? 0 : Infinity;
            } else {
                V = Math.sqrt(P * R);
                I = Math.sqrt(P / R);
            }
        }

        return {
            voltage: V,
            current: I,
            resistance: R,
            power: P,
            formatted: {
                voltage: formatValue(V, 'V'),
                current: formatValue(I, 'A'),
                resistance: formatValue(R, 'Ω'),
                power: formatValue(P, 'W')
            }
        };
    }

    function isValid(val) {
        return val !== undefined && val !== null && val !== '' && !isNaN(val);
    }

    /**
     * Format a value with appropriate SI prefix
     * @param {number} value - The value to format
     * @param {string} unit - The unit symbol
     * @returns {string} - Formatted string
     */
    function formatValue(value, unit) {
        if (value === Infinity) return '∞ ' + unit;
        if (value === 0) return '0 ' + unit;
        if (isNaN(value)) return '- ' + unit;

        const prefixes = [
            { threshold: 1e12, prefix: 'T', divisor: 1e12 },
            { threshold: 1e9, prefix: 'G', divisor: 1e9 },
            { threshold: 1e6, prefix: 'M', divisor: 1e6 },
            { threshold: 1e3, prefix: 'k', divisor: 1e3 },
            { threshold: 1, prefix: '', divisor: 1 },
            { threshold: 1e-3, prefix: 'm', divisor: 1e-3 },
            { threshold: 1e-6, prefix: 'μ', divisor: 1e-6 },
            { threshold: 1e-9, prefix: 'n', divisor: 1e-9 },
            { threshold: 1e-12, prefix: 'p', divisor: 1e-12 }
        ];

        for (const p of prefixes) {
            if (Math.abs(value) >= p.threshold) {
                const formatted = (value / p.divisor).toPrecision(4).replace(/\.?0+$/, '');
                return formatted + ' ' + p.prefix + unit;
            }
        }

        return value.toPrecision(4).replace(/\.?0+$/, '') + ' ' + unit;
    }

    // Public API
    return {
        calculate: calculate,
        formatValue: formatValue
    };
})();

// Export for Node.js/testing environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OhmsLaw;
}
