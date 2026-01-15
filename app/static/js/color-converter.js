/**
 * Color Converter Library
 * Provides functions to convert between different color spaces.
 */

const ColorConverter = (function() {
    'use strict';

    /**
     * Parse hex color string to RGB object
     * @param {string} hex - Hex color string (without #)
     * @returns {{r: number, g: number, b: number}}
     */
    function hexToRgb(hex) {
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        return { r, g, b };
    }

    /**
     * Convert RGB to hex string
     * @param {number} r - Red (0-255)
     * @param {number} g - Green (0-255)
     * @param {number} b - Blue (0-255)
     * @returns {string} Hex color string (without #)
     */
    function rgbToHex(r, g, b) {
        return r.toString(16).padStart(2, '0') +
               g.toString(16).padStart(2, '0') +
               b.toString(16).padStart(2, '0');
    }

    /**
     * Convert RGB to HSL
     * @param {number} r - Red (0-255)
     * @param {number} g - Green (0-255)
     * @param {number} b - Blue (0-255)
     * @returns {{h: number, s: number, l: number}} HSL values (h: 0-360, s: 0-100, l: 0-100)
     */
    function rgbToHsl(r, g, b) {
        r /= 255; g /= 255; b /= 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;

        if (max === min) {
            h = s = 0;
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch (max) {
                case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
                case g: h = ((b - r) / d + 2) / 6; break;
                case b: h = ((r - g) / d + 4) / 6; break;
            }
        }
        return { h: Math.round(h * 360), s: Math.round(s * 100), l: Math.round(l * 100) };
    }

    /**
     * Convert RGB to HSV
     * @param {number} r - Red (0-255)
     * @param {number} g - Green (0-255)
     * @param {number} b - Blue (0-255)
     * @returns {{h: number, s: number, v: number}} HSV values (h: 0-360, s: 0-100, v: 0-100)
     */
    function rgbToHsv(r, g, b) {
        r /= 255; g /= 255; b /= 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        let h, s, v = max;

        const d = max - min;
        s = max === 0 ? 0 : d / max;

        if (max === min) {
            h = 0;
        } else {
            switch (max) {
                case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
                case g: h = ((b - r) / d + 2) / 6; break;
                case b: h = ((r - g) / d + 4) / 6; break;
            }
        }
        return { h: Math.round(h * 360), s: Math.round(s * 100), v: Math.round(v * 100) };
    }

    /**
     * Convert RGB to CMYK
     * @param {number} r - Red (0-255)
     * @param {number} g - Green (0-255)
     * @param {number} b - Blue (0-255)
     * @returns {{c: number, m: number, y: number, k: number}} CMYK values (0-100)
     */
    function rgbToCmyk(r, g, b) {
        r /= 255; g /= 255; b /= 255;
        const k = 1 - Math.max(r, g, b);
        const c = k === 1 ? 0 : (1 - r - k) / (1 - k);
        const m = k === 1 ? 0 : (1 - g - k) / (1 - k);
        const y = k === 1 ? 0 : (1 - b - k) / (1 - k);
        return { 
            c: Math.round(c * 100), 
            m: Math.round(m * 100), 
            y: Math.round(y * 100), 
            k: Math.round(k * 100) 
        };
    }

    /**
     * Convert RGB to XYZ (CIE 1931)
     * @param {number} r - Red (0-255)
     * @param {number} g - Green (0-255)
     * @param {number} b - Blue (0-255)
     * @returns {{x: number, y: number, z: number}} XYZ values
     */
    function rgbToXyz(r, g, b) {
        r /= 255; g /= 255; b /= 255;
        
        r = r > 0.04045 ? Math.pow((r + 0.055) / 1.055, 2.4) : r / 12.92;
        g = g > 0.04045 ? Math.pow((g + 0.055) / 1.055, 2.4) : g / 12.92;
        b = b > 0.04045 ? Math.pow((b + 0.055) / 1.055, 2.4) : b / 12.92;
        
        r *= 100; g *= 100; b *= 100;
        
        const x = r * 0.4124 + g * 0.3576 + b * 0.1805;
        const y = r * 0.2126 + g * 0.7152 + b * 0.0722;
        const z = r * 0.0193 + g * 0.1192 + b * 0.9505;
        
        return { x: parseFloat(x.toFixed(2)), y: parseFloat(y.toFixed(2)), z: parseFloat(z.toFixed(2)) };
    }

    /**
     * Convert XYZ to Yxy
     * @param {number} x - X value
     * @param {number} y - Y value
     * @param {number} z - Z value
     * @returns {{Y: number, x: number, y: number}} Yxy values
     */
    function xyzToYxy(x, y, z) {
        const sum = x + y + z;
        if (sum === 0) return { Y: 0, x: 0, y: 0 };
        return {
            Y: parseFloat(y.toFixed(2)),
            x: parseFloat((x / sum).toFixed(4)),
            y: parseFloat((y / sum).toFixed(4))
        };
    }

    /**
     * Convert XYZ to Hunter Lab
     * @param {number} x - X value
     * @param {number} y - Y value
     * @param {number} z - Z value
     * @returns {{L: number, a: number, b: number}} Hunter Lab values
     */
    function xyzToHunterLab(x, y, z) {
        const sqrtY = Math.sqrt(y);
        const L = 10 * sqrtY;
        const a = sqrtY === 0 ? 0 : 17.5 * (((1.02 * x) - y) / sqrtY);
        const b = sqrtY === 0 ? 0 : 7 * ((y - (0.847 * z)) / sqrtY);
        return { L: parseFloat(L.toFixed(2)), a: parseFloat(a.toFixed(2)), b: parseFloat(b.toFixed(2)) };
    }

    /**
     * Convert XYZ to CIE-Lab (D65 illuminant)
     * @param {number} x - X value
     * @param {number} y - Y value
     * @param {number} z - Z value
     * @returns {{L: number, a: number, b: number}} CIE-Lab values
     */
    function xyzToCieLab(x, y, z) {
        // D65 reference white
        const refX = 95.047, refY = 100.000, refZ = 108.883;
        
        x = x / refX;
        y = y / refY;
        z = z / refZ;
        
        x = x > 0.008856 ? Math.pow(x, 1/3) : (7.787 * x) + (16/116);
        y = y > 0.008856 ? Math.pow(y, 1/3) : (7.787 * y) + (16/116);
        z = z > 0.008856 ? Math.pow(z, 1/3) : (7.787 * z) + (16/116);
        
        const L = (116 * y) - 16;
        const a = 500 * (x - y);
        const b = 200 * (y - z);
        
        return { L: parseFloat(L.toFixed(2)), a: parseFloat(a.toFixed(2)), b: parseFloat(b.toFixed(2)) };
    }

    /**
     * Convert RGB to Yxy (via XYZ)
     * @param {number} r - Red (0-255)
     * @param {number} g - Green (0-255)
     * @param {number} b - Blue (0-255)
     * @returns {{Y: number, x: number, y: number}} Yxy values
     */
    function rgbToYxy(r, g, b) {
        const xyz = rgbToXyz(r, g, b);
        return xyzToYxy(xyz.x, xyz.y, xyz.z);
    }

    /**
     * Convert RGB to Hunter Lab (via XYZ)
     * @param {number} r - Red (0-255)
     * @param {number} g - Green (0-255)
     * @param {number} b - Blue (0-255)
     * @returns {{L: number, a: number, b: number}} Hunter Lab values
     */
    function rgbToHunterLab(r, g, b) {
        const xyz = rgbToXyz(r, g, b);
        return xyzToHunterLab(xyz.x, xyz.y, xyz.z);
    }

    /**
     * Convert RGB to CIE-Lab (via XYZ)
     * @param {number} r - Red (0-255)
     * @param {number} g - Green (0-255)
     * @param {number} b - Blue (0-255)
     * @returns {{L: number, a: number, b: number}} CIE-Lab values
     */
    function rgbToCieLab(r, g, b) {
        const xyz = rgbToXyz(r, g, b);
        return xyzToCieLab(xyz.x, xyz.y, xyz.z);
    }

    /**
     * Generate tint (lighter variation) of a color
     * @param {number} r - Red (0-255)
     * @param {number} g - Green (0-255)
     * @param {number} b - Blue (0-255)
     * @param {number} factor - Tint factor (0-1, where 1 is white)
     * @returns {{r: number, g: number, b: number}}
     */
    function generateTint(r, g, b, factor) {
        return {
            r: Math.round(r + ((255 - r) * factor)),
            g: Math.round(g + ((255 - g) * factor)),
            b: Math.round(b + ((255 - b) * factor))
        };
    }

    /**
     * Generate shade (darker variation) of a color
     * @param {number} r - Red (0-255)
     * @param {number} g - Green (0-255)
     * @param {number} b - Blue (0-255)
     * @param {number} factor - Shade factor (0-1, where 1 is black)
     * @returns {{r: number, g: number, b: number}}
     */
    function generateShade(r, g, b, factor) {
        return {
            r: Math.round(r * (1 - factor)),
            g: Math.round(g * (1 - factor)),
            b: Math.round(b * (1 - factor))
        };
    }

    // Public API
    return {
        hexToRgb: hexToRgb,
        rgbToHex: rgbToHex,
        rgbToHsl: rgbToHsl,
        rgbToHsv: rgbToHsv,
        rgbToCmyk: rgbToCmyk,
        rgbToXyz: rgbToXyz,
        rgbToYxy: rgbToYxy,
        rgbToHunterLab: rgbToHunterLab,
        rgbToCieLab: rgbToCieLab,
        xyzToYxy: xyzToYxy,
        xyzToHunterLab: xyzToHunterLab,
        xyzToCieLab: xyzToCieLab,
        generateTint: generateTint,
        generateShade: generateShade
    };
})();

// Export for Node.js testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ColorConverter;
}
