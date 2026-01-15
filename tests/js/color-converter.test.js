/**
 * Tests for Color Converter Library
 * Run with: node color-converter.test.js
 */

const ColorConverter = require('../../app/static/js/color-converter.js');

let passed = 0;
let failed = 0;

function assert(condition, message) {
    if (condition) {
        passed++;
        console.log(`✓ ${message}`);
    } else {
        failed++;
        console.log(`✗ ${message}`);
    }
}

function assertClose(actual, expected, tolerance, message) {
    const diff = Math.abs(actual - expected);
    if (diff <= tolerance) {
        passed++;
        console.log(`✓ ${message}`);
    } else {
        failed++;
        console.log(`✗ ${message} (expected ${expected}, got ${actual})`);
    }
}

console.log('=== Color Converter Tests ===\n');

// Test hexToRgb
console.log('--- hexToRgb ---');
let rgb = ColorConverter.hexToRgb('FF0000');
assert(rgb.r === 255 && rgb.g === 0 && rgb.b === 0, 'hexToRgb: red');

rgb = ColorConverter.hexToRgb('00FF00');
assert(rgb.r === 0 && rgb.g === 255 && rgb.b === 0, 'hexToRgb: green');

rgb = ColorConverter.hexToRgb('0000FF');
assert(rgb.r === 0 && rgb.g === 0 && rgb.b === 255, 'hexToRgb: blue');

rgb = ColorConverter.hexToRgb('000000');
assert(rgb.r === 0 && rgb.g === 0 && rgb.b === 0, 'hexToRgb: black');

rgb = ColorConverter.hexToRgb('FFFFFF');
assert(rgb.r === 255 && rgb.g === 255 && rgb.b === 255, 'hexToRgb: white');

rgb = ColorConverter.hexToRgb('4A90E2');
assert(rgb.r === 74 && rgb.g === 144 && rgb.b === 226, 'hexToRgb: custom blue');

// Test rgbToHex
console.log('\n--- rgbToHex ---');
assert(ColorConverter.rgbToHex(255, 0, 0) === 'ff0000', 'rgbToHex: red');
assert(ColorConverter.rgbToHex(0, 255, 0) === '00ff00', 'rgbToHex: green');
assert(ColorConverter.rgbToHex(0, 0, 255) === '0000ff', 'rgbToHex: blue');
assert(ColorConverter.rgbToHex(0, 0, 0) === '000000', 'rgbToHex: black');
assert(ColorConverter.rgbToHex(255, 255, 255) === 'ffffff', 'rgbToHex: white');

// Test rgbToHsl
console.log('\n--- rgbToHsl ---');
let hsl = ColorConverter.rgbToHsl(255, 0, 0);
assert(hsl.h === 0 && hsl.s === 100 && hsl.l === 50, 'rgbToHsl: red');

hsl = ColorConverter.rgbToHsl(0, 255, 0);
assert(hsl.h === 120 && hsl.s === 100 && hsl.l === 50, 'rgbToHsl: green');

hsl = ColorConverter.rgbToHsl(0, 0, 255);
assert(hsl.h === 240 && hsl.s === 100 && hsl.l === 50, 'rgbToHsl: blue');

hsl = ColorConverter.rgbToHsl(0, 0, 0);
assert(hsl.h === 0 && hsl.s === 0 && hsl.l === 0, 'rgbToHsl: black');

hsl = ColorConverter.rgbToHsl(255, 255, 255);
assert(hsl.h === 0 && hsl.s === 0 && hsl.l === 100, 'rgbToHsl: white');

hsl = ColorConverter.rgbToHsl(128, 128, 128);
assert(hsl.h === 0 && hsl.s === 0 && hsl.l === 50, 'rgbToHsl: gray');

// Test rgbToHsv
console.log('\n--- rgbToHsv ---');
let hsv = ColorConverter.rgbToHsv(255, 0, 0);
assert(hsv.h === 0 && hsv.s === 100 && hsv.v === 100, 'rgbToHsv: red');

hsv = ColorConverter.rgbToHsv(0, 255, 0);
assert(hsv.h === 120 && hsv.s === 100 && hsv.v === 100, 'rgbToHsv: green');

hsv = ColorConverter.rgbToHsv(0, 0, 255);
assert(hsv.h === 240 && hsv.s === 100 && hsv.v === 100, 'rgbToHsv: blue');

hsv = ColorConverter.rgbToHsv(0, 0, 0);
assert(hsv.h === 0 && hsv.s === 0 && hsv.v === 0, 'rgbToHsv: black');

hsv = ColorConverter.rgbToHsv(255, 255, 255);
assert(hsv.h === 0 && hsv.s === 0 && hsv.v === 100, 'rgbToHsv: white');

// Test rgbToCmyk
console.log('\n--- rgbToCmyk ---');
let cmyk = ColorConverter.rgbToCmyk(255, 0, 0);
assert(cmyk.c === 0 && cmyk.m === 100 && cmyk.y === 100 && cmyk.k === 0, 'rgbToCmyk: red');

cmyk = ColorConverter.rgbToCmyk(0, 255, 0);
assert(cmyk.c === 100 && cmyk.m === 0 && cmyk.y === 100 && cmyk.k === 0, 'rgbToCmyk: green');

cmyk = ColorConverter.rgbToCmyk(0, 0, 255);
assert(cmyk.c === 100 && cmyk.m === 100 && cmyk.y === 0 && cmyk.k === 0, 'rgbToCmyk: blue');

cmyk = ColorConverter.rgbToCmyk(0, 0, 0);
assert(cmyk.c === 0 && cmyk.m === 0 && cmyk.y === 0 && cmyk.k === 100, 'rgbToCmyk: black');

cmyk = ColorConverter.rgbToCmyk(255, 255, 255);
assert(cmyk.c === 0 && cmyk.m === 0 && cmyk.y === 0 && cmyk.k === 0, 'rgbToCmyk: white');

// Test rgbToXyz
console.log('\n--- rgbToXyz ---');
let xyz = ColorConverter.rgbToXyz(255, 0, 0);
assertClose(xyz.x, 41.24, 0.1, 'rgbToXyz: red X');
assertClose(xyz.y, 21.26, 0.1, 'rgbToXyz: red Y');
assertClose(xyz.z, 1.93, 0.1, 'rgbToXyz: red Z');

xyz = ColorConverter.rgbToXyz(0, 0, 0);
assert(xyz.x === 0 && xyz.y === 0 && xyz.z === 0, 'rgbToXyz: black');

// Test generateTint
console.log('\n--- generateTint ---');
let tint = ColorConverter.generateTint(100, 100, 100, 0.5);
assert(tint.r === 178 && tint.g === 178 && tint.b === 178, 'generateTint: 50% tint of gray');

tint = ColorConverter.generateTint(255, 0, 0, 0.5);
assert(tint.r === 255 && tint.g === 128 && tint.b === 128, 'generateTint: 50% tint of red');

tint = ColorConverter.generateTint(0, 0, 0, 1);
assert(tint.r === 255 && tint.g === 255 && tint.b === 255, 'generateTint: 100% tint is white');

// Test generateShade
console.log('\n--- generateShade ---');
let shade = ColorConverter.generateShade(100, 100, 100, 0.5);
assert(shade.r === 50 && shade.g === 50 && shade.b === 50, 'generateShade: 50% shade of gray');

shade = ColorConverter.generateShade(255, 0, 0, 0.5);
assert(shade.r === 128 && shade.g === 0 && shade.b === 0, 'generateShade: 50% shade of red');

shade = ColorConverter.generateShade(255, 255, 255, 1);
assert(shade.r === 0 && shade.g === 0 && shade.b === 0, 'generateShade: 100% shade is black');

// Test rgbToYxy
console.log('\n--- rgbToYxy ---');
let yxy = ColorConverter.rgbToYxy(255, 0, 0);
assertClose(yxy.Y, 21.26, 0.1, 'rgbToYxy: red Y');

// Test rgbToHunterLab
console.log('\n--- rgbToHunterLab ---');
let hunterLab = ColorConverter.rgbToHunterLab(255, 0, 0);
assertClose(hunterLab.L, 46.11, 0.2, 'rgbToHunterLab: red L');

// Test rgbToCieLab
console.log('\n--- rgbToCieLab ---');
let cieLab = ColorConverter.rgbToCieLab(255, 0, 0);
assertClose(cieLab.L, 53.23, 0.2, 'rgbToCieLab: red L');
assertClose(cieLab.a, 80.11, 0.2, 'rgbToCieLab: red a');
assertClose(cieLab.b, 67.22, 0.2, 'rgbToCieLab: red b');

// Test with reference value #123456
console.log('\n--- Reference Color #123456 ---');
rgb = ColorConverter.hexToRgb('123456');
assert(rgb.r === 18 && rgb.g === 52 && rgb.b === 86, '#123456 hexToRgb');

hsl = ColorConverter.rgbToHsl(18, 52, 86);
assert(hsl.h === 210 && hsl.s === 65 && hsl.l === 20, '#123456 rgbToHsl');

hsv = ColorConverter.rgbToHsv(18, 52, 86);
assert(hsv.h === 210 && hsv.s === 79 && hsv.v === 34, '#123456 rgbToHsv');

cmyk = ColorConverter.rgbToCmyk(18, 52, 86);
assert(cmyk.c === 79 && cmyk.m === 40 && cmyk.y === 0 && cmyk.k === 66, '#123456 rgbToCmyk');

xyz = ColorConverter.rgbToXyz(18, 52, 86);
assertClose(xyz.x, 3.16, 0.01, '#123456 rgbToXyz X');
assertClose(xyz.y, 3.26, 0.01, '#123456 rgbToXyz Y');
assertClose(xyz.z, 9.27, 0.01, '#123456 rgbToXyz Z');

yxy = ColorConverter.rgbToYxy(18, 52, 86);
assertClose(yxy.Y, 3.26, 0.01, '#123456 rgbToYxy Y');
assertClose(yxy.x, 0.2014, 0.001, '#123456 rgbToYxy x');
assertClose(yxy.y, 0.2078, 0.001, '#123456 rgbToYxy y');

hunterLab = ColorConverter.rgbToHunterLab(18, 52, 86);
assertClose(hunterLab.L, 18.05, 0.1, '#123456 Hunter Lab L');
assertClose(hunterLab.a, -0.35, 0.1, '#123456 Hunter Lab a');
assertClose(hunterLab.b, -17.81, 0.1, '#123456 Hunter Lab b');

cieLab = ColorConverter.rgbToCieLab(18, 52, 86);
assertClose(cieLab.L, 21.04, 0.1, '#123456 CIE-Lab L');
assertClose(cieLab.a, 1.06, 0.1, '#123456 CIE-Lab a');
assertClose(cieLab.b, -24.10, 0.1, '#123456 CIE-Lab b');

// Test with reference value #112233
console.log('\n--- Reference Color #112233 ---');
rgb = ColorConverter.hexToRgb('112233');
assert(rgb.r === 17 && rgb.g === 34 && rgb.b === 51, '#112233 hexToRgb');

hsl = ColorConverter.rgbToHsl(17, 34, 51);
assert(hsl.h === 210 && hsl.s === 50 && hsl.l === 13, '#112233 rgbToHsl');

hsv = ColorConverter.rgbToHsv(17, 34, 51);
assert(hsv.h === 210 && hsv.s === 67 && hsv.v === 20, '#112233 rgbToHsv');

cmyk = ColorConverter.rgbToCmyk(17, 34, 51);
assert(cmyk.c === 67 && cmyk.m === 33 && cmyk.y === 0 && cmyk.k === 80, '#112233 rgbToCmyk');

xyz = ColorConverter.rgbToXyz(17, 34, 51);
assertClose(xyz.x, 1.40, 0.02, '#112233 rgbToXyz X');
assertClose(xyz.y, 1.50, 0.02, '#112233 rgbToXyz Y');
assertClose(xyz.z, 3.35, 0.02, '#112233 rgbToXyz Z');

yxy = ColorConverter.rgbToYxy(17, 34, 51);
assertClose(yxy.Y, 1.50, 0.02, '#112233 rgbToYxy Y');
assertClose(yxy.x, 0.2241, 0.001, '#112233 rgbToYxy x');
assertClose(yxy.y, 0.2403, 0.001, '#112233 rgbToYxy y');

hunterLab = ColorConverter.rgbToHunterLab(17, 34, 51);
assertClose(hunterLab.L, 12.26, 0.1, '#112233 Hunter Lab L');
assertClose(hunterLab.a, -1.05, 0.1, '#112233 Hunter Lab a');
assertClose(hunterLab.b, -7.62, 0.1, '#112233 Hunter Lab b');

cieLab = ColorConverter.rgbToCieLab(17, 34, 51);
assertClose(cieLab.L, 12.62, 0.1, '#112233 CIE-Lab L');
assertClose(cieLab.a, -0.79, 0.1, '#112233 CIE-Lab a');
assertClose(cieLab.b, -13.31, 0.1, '#112233 CIE-Lab b');

// Test with reference value #ab16dd
console.log('\n--- Reference Color #ab16dd ---');
rgb = ColorConverter.hexToRgb('ab16dd');
assert(rgb.r === 171 && rgb.g === 22 && rgb.b === 221, '#ab16dd hexToRgb');

hsl = ColorConverter.rgbToHsl(171, 22, 221);
assert(hsl.h === 285 && hsl.s === 82 && hsl.l === 48, '#ab16dd rgbToHsl');

hsv = ColorConverter.rgbToHsv(171, 22, 221);
assert(hsv.h === 285 && hsv.s === 90 && hsv.v === 87, '#ab16dd rgbToHsv');

cmyk = ColorConverter.rgbToCmyk(171, 22, 221);
assert(cmyk.c === 23 && cmyk.m === 90 && cmyk.y === 0 && cmyk.k === 13, '#ab16dd rgbToCmyk');

xyz = ColorConverter.rgbToXyz(171, 22, 221);
assertClose(xyz.x, 30.13, 0.1, '#ab16dd rgbToXyz X');
assertClose(xyz.y, 14.45, 0.1, '#ab16dd rgbToXyz Y');
assertClose(xyz.z, 69.61, 0.1, '#ab16dd rgbToXyz Z');

yxy = ColorConverter.rgbToYxy(171, 22, 221);
assertClose(yxy.Y, 14.45, 0.1, '#ab16dd rgbToYxy Y');
assertClose(yxy.x, 0.2639, 0.001, '#ab16dd rgbToYxy x');
assertClose(yxy.y, 0.1266, 0.001, '#ab16dd rgbToYxy y');

hunterLab = ColorConverter.rgbToHunterLab(171, 22, 221);
assertClose(hunterLab.L, 38.02, 0.1, '#ab16dd Hunter Lab L');
assertClose(hunterLab.a, 74.96, 0.2, '#ab16dd Hunter Lab a');
assertClose(hunterLab.b, -81.95, 0.2, '#ab16dd Hunter Lab b');

cieLab = ColorConverter.rgbToCieLab(171, 22, 221);
assertClose(cieLab.L, 44.87, 0.1, '#ab16dd CIE-Lab L');
assertClose(cieLab.a, 78.54, 0.2, '#ab16dd CIE-Lab a');
assertClose(cieLab.b, -67.34, 0.2, '#ab16dd CIE-Lab b');

// Summary
console.log('\n=== Test Summary ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log(`Total: ${passed + failed}`);

process.exit(failed > 0 ? 1 : 0);
