/**
 * Tests for Ohm's Law Calculator Library
 * Run with: node tests/js/ohms-law.test.js
 */

const OhmsLaw = require('../../app/static/js/ohms-law.js');

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

function assertApprox(actual, expected, tolerance = 0.001, msg = '') {
    if (Math.abs(actual - expected) > tolerance) {
        throw new Error(`${msg}\n  Expected: ${expected}\n  Actual: ${actual}\n  Tolerance: ${tolerance}`);
    }
}

function assertEqual(actual, expected, msg = '') {
    if (actual !== expected) {
        throw new Error(`${msg}\n  Expected: ${expected}\n  Actual: ${actual}`);
    }
}

console.log('=== Ohm\'s Law Calculator Tests ===\n');

// ============================================
// V = I × R Tests
// ============================================

console.log('--- V = I × R Tests ---\n');

test('V and I known: 12V, 2A → R=6Ω, P=24W', () => {
    const result = OhmsLaw.calculate({ voltage: 12, current: 2 });
    assertApprox(result.voltage, 12);
    assertApprox(result.current, 2);
    assertApprox(result.resistance, 6);
    assertApprox(result.power, 24);
});

test('V and R known: 12V, 6Ω → I=2A, P=24W', () => {
    const result = OhmsLaw.calculate({ voltage: 12, resistance: 6 });
    assertApprox(result.voltage, 12);
    assertApprox(result.current, 2);
    assertApprox(result.resistance, 6);
    assertApprox(result.power, 24);
});

test('I and R known: 2A, 6Ω → V=12V, P=24W', () => {
    const result = OhmsLaw.calculate({ current: 2, resistance: 6 });
    assertApprox(result.voltage, 12);
    assertApprox(result.current, 2);
    assertApprox(result.resistance, 6);
    assertApprox(result.power, 24);
});

// ============================================
// P = V × I Tests
// ============================================

console.log('\n--- P = V × I Tests ---\n');

test('V and P known: 12V, 24W → I=2A, R=6Ω', () => {
    const result = OhmsLaw.calculate({ voltage: 12, power: 24 });
    assertApprox(result.voltage, 12);
    assertApprox(result.current, 2);
    assertApprox(result.resistance, 6);
    assertApprox(result.power, 24);
});

test('I and P known: 2A, 24W → V=12V, R=6Ω', () => {
    const result = OhmsLaw.calculate({ current: 2, power: 24 });
    assertApprox(result.voltage, 12);
    assertApprox(result.current, 2);
    assertApprox(result.resistance, 6);
    assertApprox(result.power, 24);
});

test('R and P known: 6Ω, 24W → V=12V, I=2A', () => {
    const result = OhmsLaw.calculate({ resistance: 6, power: 24 });
    assertApprox(result.voltage, 12);
    assertApprox(result.current, 2);
    assertApprox(result.resistance, 6);
    assertApprox(result.power, 24);
});

// ============================================
// Real-world Examples
// ============================================

console.log('\n--- Real-world Examples ---\n');

test('LED circuit: 5V supply, 20mA LED, need resistor', () => {
    // LED forward voltage ~2V, so 3V across resistor at 20mA
    const result = OhmsLaw.calculate({ voltage: 3, current: 0.02 });
    assertApprox(result.resistance, 150);
    assertApprox(result.power, 0.06);
});

test('USB charger: 5V, 2.4A output', () => {
    const result = OhmsLaw.calculate({ voltage: 5, current: 2.4 });
    assertApprox(result.power, 12);
});

test('100W light bulb at 120V', () => {
    const result = OhmsLaw.calculate({ voltage: 120, power: 100 });
    assertApprox(result.current, 0.833, 0.01);
    assertApprox(result.resistance, 144, 1);
});

test('Car battery: 12V, 1kΩ load', () => {
    const result = OhmsLaw.calculate({ voltage: 12, resistance: 1000 });
    assertApprox(result.current, 0.012);
    assertApprox(result.power, 0.144);
});

// ============================================
// Edge Cases
// ============================================

console.log('\n--- Edge Cases ---\n');

test('Zero current: V=12, I=0 → R=∞, P=0', () => {
    const result = OhmsLaw.calculate({ voltage: 12, current: 0 });
    assertEqual(result.resistance, Infinity);
    assertEqual(result.power, 0);
});

test('Zero resistance: V=12, R=0 → I=∞, P=∞', () => {
    const result = OhmsLaw.calculate({ voltage: 12, resistance: 0 });
    assertEqual(result.current, Infinity);
    assertEqual(result.power, Infinity);
});

test('String inputs are parsed: "12", "2"', () => {
    const result = OhmsLaw.calculate({ voltage: "12", current: "2" });
    assertApprox(result.resistance, 6);
    assertApprox(result.power, 24);
});

// ============================================
// Formatting Tests
// ============================================

console.log('\n--- Formatting Tests ---\n');

test('Format milliamps: 0.001A', () => {
    const formatted = OhmsLaw.formatValue(0.001, 'A');
    assertEqual(formatted, '1 mA');
});

test('Format kilohms: 1000Ω', () => {
    const formatted = OhmsLaw.formatValue(1000, 'Ω');
    assertEqual(formatted, '1 kΩ');
});

test('Format megohms: 1000000Ω', () => {
    const formatted = OhmsLaw.formatValue(1000000, 'Ω');
    assertEqual(formatted, '1 MΩ');
});

test('Format milliwatts: 0.05W', () => {
    const formatted = OhmsLaw.formatValue(0.05, 'W');
    assertEqual(formatted, '50 mW');
});

// ============================================
// Error Handling Tests
// ============================================

console.log('\n--- Error Handling Tests ---\n');

test('Error: Only one value provided', () => {
    try {
        OhmsLaw.calculate({ voltage: 12 });
        throw new Error('Should have thrown an error');
    } catch (e) {
        if (!e.message.includes('At least two values')) {
            throw e;
        }
    }
});

test('Error: No values provided', () => {
    try {
        OhmsLaw.calculate({});
        throw new Error('Should have thrown an error');
    } catch (e) {
        if (!e.message.includes('At least two values')) {
            throw e;
        }
    }
});

test('Error: Negative voltage', () => {
    try {
        OhmsLaw.calculate({ voltage: -12, current: 2 });
        throw new Error('Should have thrown an error');
    } catch (e) {
        if (!e.message.includes('non-negative')) {
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
