/**
 * Tests for Resistor Color Code Calculator Library
 * Run with: node tests/js/resistor-calculator.test.js
 */

const ResistorCalculator = require('../../app/static/js/resistor-calculator.js');

let passed = 0;
let failed = 0;

function test(name, fn) {
    try {
        fn();
        console.log(`✓ ${name}`);
        passed++;
    } catch (e) {
        console.log(`✗ ${name}`);
        console.log(`  Error: ${e.message}`);
        failed++;
    }
}

function assertEqual(actual, expected, msg = '') {
    const actualStr = JSON.stringify(actual);
    const expectedStr = JSON.stringify(expected);
    if (actualStr !== expectedStr) {
        throw new Error(`${msg}\n  Expected: ${expectedStr}\n  Actual: ${actualStr}`);
    }
}

function assertApprox(actual, expected, tolerance = 0.001, msg = '') {
    if (Math.abs(actual - expected) > tolerance) {
        throw new Error(`${msg}\n  Expected: ${expected}\n  Actual: ${actual}\n  Tolerance: ${tolerance}`);
    }
}

console.log('=== Resistor Color Code Calculator Tests ===\n');

// ============================================
// Wikipedia Examples
// ============================================

console.log('--- Wikipedia Examples ---\n');

test('Wikipedia: Green-Blue-Black-Black-Brown = 560 Ω ±1%', () => {
    const result = ResistorCalculator.calculate(['green', 'blue', 'black', 'black', 'brown']);
    assertEqual(result.resistance, 560);
    assertEqual(result.tolerance, 1);
});

test('Wikipedia: Red-Red-Orange-Gold = 22000 Ω ±5%', () => {
    const result = ResistorCalculator.calculate(['red', 'red', 'orange', 'gold']);
    assertEqual(result.resistance, 22000);
    assertEqual(result.tolerance, 5);
});

test('Wikipedia: Yellow-Violet-Brown-Gold = 470 Ω ±5%', () => {
    const result = ResistorCalculator.calculate(['yellow', 'violet', 'brown', 'gold']);
    assertEqual(result.resistance, 470);
    assertEqual(result.tolerance, 5);
});

test('Wikipedia: Blue-Grey-Black-Gold = 68 Ω ±5%', () => {
    const result = ResistorCalculator.calculate(['blue', 'grey', 'black', 'gold']);
    assertEqual(result.resistance, 68);
    assertEqual(result.tolerance, 5);
});

// ============================================
// Web Examples
// ============================================

console.log('\n--- Web Examples ---\n');

test('Example 1: Yellow-Violet-Orange-Gold = 47 kΩ ±5%', () => {
    const result = ResistorCalculator.calculate(['yellow', 'violet', 'orange', 'gold']);
    assertEqual(result.resistance, 47000);
    assertEqual(result.tolerance, 5);
    assertEqual(result.formatted, '47 kΩ');
});

test('Example 2: Green-Red-Gold-Silver = 5.2 Ω ±10%', () => {
    const result = ResistorCalculator.calculate(['green', 'red', 'gold', 'silver']);
    assertApprox(result.resistance, 5.2);
    assertEqual(result.tolerance, 10);
});

test('Example 3: White-Violet-Black = 97 Ω ±20% (3-band)', () => {
    const result = ResistorCalculator.calculate(['white', 'violet', 'black']);
    assertEqual(result.resistance, 97);
    assertEqual(result.tolerance, 20);
});

test('Example 4: Orange-Orange-Black-Brown-Violet = 3.3 kΩ ±0.1%', () => {
    const result = ResistorCalculator.calculate(['orange', 'orange', 'black', 'brown', 'violet']);
    assertEqual(result.resistance, 3300);
    assertEqual(result.tolerance, 0.1);
});

test('Example 5: Brown-Green-Grey-Silver-Red = 1.58 Ω ±2%', () => {
    const result = ResistorCalculator.calculate(['brown', 'green', 'grey', 'silver', 'red']);
    assertApprox(result.resistance, 1.58);
    assertEqual(result.tolerance, 2);
});

test('Example 6: Blue-Brown-Green-Silver-Blue = 6.15 Ω ±0.25%', () => {
    const result = ResistorCalculator.calculate(['blue', 'brown', 'green', 'silver', 'blue']);
    assertApprox(result.resistance, 6.15);
    assertEqual(result.tolerance, 0.25);
});

// ============================================
// Additional Tests
// ============================================

console.log('\n--- Additional Tests ---\n');

test('3-band: Brown-Black-Red = 1000 Ω ±20%', () => {
    const result = ResistorCalculator.calculate(['brown', 'black', 'red']);
    assertEqual(result.resistance, 1000);
    assertEqual(result.tolerance, 20);
});

test('4-band: Brown-Black-Orange-Gold = 10 kΩ ±5%', () => {
    const result = ResistorCalculator.calculate(['brown', 'black', 'orange', 'gold']);
    assertEqual(result.resistance, 10000);
    assertEqual(result.tolerance, 5);
});

test('5-band: Brown-Black-Black-Red-Brown = 10 kΩ ±1%', () => {
    const result = ResistorCalculator.calculate(['brown', 'black', 'black', 'red', 'brown']);
    assertEqual(result.resistance, 10000);
    assertEqual(result.tolerance, 1);
});

test('6-band with TCR: Brown-Black-Black-Brown-Brown-Brown = 1 kΩ ±1% 100ppm/K', () => {
    const result = ResistorCalculator.calculate(['brown', 'black', 'black', 'brown', 'brown', 'brown']);
    assertEqual(result.resistance, 1000);
    assertEqual(result.tolerance, 1);
    assertEqual(result.tcr, 100);
});

test('Value range calculation for 1 kΩ ±5%', () => {
    const result = ResistorCalculator.calculate(['brown', 'black', 'red', 'gold']);
    assertEqual(result.resistance, 1000);
    assertEqual(result.min, 950);
    assertEqual(result.max, 1050);
});

test('Format resistance: small values (mΩ)', () => {
    const formatted = ResistorCalculator.formatResistance(0.47);
    assertEqual(formatted, '470 mΩ');
});

test('Format resistance: ohms', () => {
    const formatted = ResistorCalculator.formatResistance(470);
    assertEqual(formatted, '470 Ω');
});

test('Format resistance: kilohms', () => {
    const formatted = ResistorCalculator.formatResistance(4700);
    assertEqual(formatted, '4.7 kΩ');
});

test('Format resistance: megohms', () => {
    const formatted = ResistorCalculator.formatResistance(4700000);
    assertEqual(formatted, '4.7 MΩ');
});

test('Format resistance: gigohms', () => {
    const formatted = ResistorCalculator.formatResistance(4700000000);
    assertEqual(formatted, '4.7 GΩ');
});

test('Case insensitivity: BROWN-BLACK-RED = 1000 Ω', () => {
    const result = ResistorCalculator.calculate(['BROWN', 'BLACK', 'RED']);
    assertEqual(result.resistance, 1000);
});

test('isValidColor: brown is valid for digit', () => {
    assertEqual(ResistorCalculator.isValidColor('brown', 'digit'), true);
});

test('isValidColor: gold is not valid for digit', () => {
    assertEqual(ResistorCalculator.isValidColor('gold', 'digit'), false);
});

test('isValidColor: gold is valid for tolerance', () => {
    assertEqual(ResistorCalculator.isValidColor('gold', 'tolerance'), true);
});

test('isValidColor: brown is valid for tcr', () => {
    assertEqual(ResistorCalculator.isValidColor('brown', 'tcr'), true);
});

// ============================================
// Error Handling Tests
// ============================================

console.log('\n--- Error Handling Tests ---\n');

test('Error: Invalid number of bands (2)', () => {
    try {
        ResistorCalculator.calculate(['brown', 'black']);
        throw new Error('Should have thrown an error');
    } catch (e) {
        if (!e.message.includes('Invalid number of bands')) {
            throw e;
        }
    }
});

test('Error: Invalid number of bands (7)', () => {
    try {
        ResistorCalculator.calculate(['brown', 'black', 'red', 'gold', 'brown', 'brown', 'brown']);
        throw new Error('Should have thrown an error');
    } catch (e) {
        if (!e.message.includes('Invalid number of bands')) {
            throw e;
        }
    }
});

test('Error: Unknown color', () => {
    try {
        ResistorCalculator.calculate(['purple', 'black', 'red']);
        throw new Error('Should have thrown an error');
    } catch (e) {
        if (!e.message.includes('Unknown color')) {
            throw e;
        }
    }
});

// ============================================
// Summary
// ============================================

console.log('\n=== Summary ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log(`Total: ${passed + failed}`);

if (failed > 0) {
    process.exit(1);
}
