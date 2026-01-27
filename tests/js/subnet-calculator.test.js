/**
 * Tests for Subnet Calculator Library
 * Run with: node tests/js/subnet-calculator.test.js
 */

const SubnetCalculator = require('../../app/static/js/subnet-calculator.js');

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
    if (actual !== expected) {
        throw new Error(`${msg}\n  Expected: ${expected}\n  Actual: ${actual}`);
    }
}

console.log('=== Subnet Calculator Tests ===\n');

// ============================================
// IPv4 Tests
// ============================================

console.log('--- IPv4 Basic Tests ---\n');

test('IPv4: 192.168.1.100/24 network address', () => {
    const result = SubnetCalculator.calculateIPv4('192.168.1.100', 24);
    assertEqual(result.networkAddress, '192.168.1.0');
});

test('IPv4: 192.168.1.100/24 broadcast address', () => {
    const result = SubnetCalculator.calculateIPv4('192.168.1.100', 24);
    assertEqual(result.broadcastAddress, '192.168.1.255');
});

test('IPv4: 192.168.1.100/24 subnet mask', () => {
    const result = SubnetCalculator.calculateIPv4('192.168.1.100', 24);
    assertEqual(result.subnetMask, '255.255.255.0');
});

test('IPv4: 192.168.1.100/24 wildcard mask', () => {
    const result = SubnetCalculator.calculateIPv4('192.168.1.100', 24);
    assertEqual(result.wildcardMask, '0.0.0.255');
});

test('IPv4: 192.168.1.100/24 host range', () => {
    const result = SubnetCalculator.calculateIPv4('192.168.1.100', 24);
    assertEqual(result.hostMin, '192.168.1.1');
    assertEqual(result.hostMax, '192.168.1.254');
});

test('IPv4: 192.168.1.100/24 usable hosts', () => {
    const result = SubnetCalculator.calculateIPv4('192.168.1.100', 24);
    assertEqual(result.usableHosts, 254);
});

test('IPv4: 192.168.1.100/24 total hosts', () => {
    const result = SubnetCalculator.calculateIPv4('192.168.1.100', 24);
    assertEqual(result.totalHosts, 256);
});

console.log('\n--- IPv4 Different Subnets ---\n');

test('IPv4: 10.0.0.1/8 network', () => {
    const result = SubnetCalculator.calculateIPv4('10.0.0.1', 8);
    assertEqual(result.networkAddress, '10.0.0.0');
    assertEqual(result.broadcastAddress, '10.255.255.255');
    assertEqual(result.usableHosts, 16777214);
});

test('IPv4: 172.16.0.1/16 network', () => {
    const result = SubnetCalculator.calculateIPv4('172.16.0.1', 16);
    assertEqual(result.networkAddress, '172.16.0.0');
    assertEqual(result.broadcastAddress, '172.16.255.255');
    assertEqual(result.usableHosts, 65534);
});

test('IPv4: 192.168.1.100/28 network', () => {
    const result = SubnetCalculator.calculateIPv4('192.168.1.100', 28);
    assertEqual(result.networkAddress, '192.168.1.96');
    assertEqual(result.broadcastAddress, '192.168.1.111');
    assertEqual(result.usableHosts, 14);
});

test('IPv4: 192.168.1.100/30 (point-to-point)', () => {
    const result = SubnetCalculator.calculateIPv4('192.168.1.100', 30);
    assertEqual(result.networkAddress, '192.168.1.100');
    assertEqual(result.broadcastAddress, '192.168.1.103');
    assertEqual(result.usableHosts, 2);
});

console.log('\n--- IPv4 Class Detection ---\n');

test('IPv4: Class A (10.x.x.x)', () => {
    const result = SubnetCalculator.calculateIPv4('10.0.0.1', 8);
    assertEqual(result.ipClass, 'A');
});

test('IPv4: Class B (172.16.x.x)', () => {
    const result = SubnetCalculator.calculateIPv4('172.16.0.1', 16);
    assertEqual(result.ipClass, 'B');
});

test('IPv4: Class C (192.168.x.x)', () => {
    const result = SubnetCalculator.calculateIPv4('192.168.1.1', 24);
    assertEqual(result.ipClass, 'C');
});

console.log('\n--- IPv4 Private Detection ---\n');

test('IPv4: 10.x.x.x is private', () => {
    const result = SubnetCalculator.calculateIPv4('10.0.0.1', 8);
    assertEqual(result.isPrivate, true);
});

test('IPv4: 172.16.x.x is private', () => {
    const result = SubnetCalculator.calculateIPv4('172.16.0.1', 12);
    assertEqual(result.isPrivate, true);
});

test('IPv4: 192.168.x.x is private', () => {
    const result = SubnetCalculator.calculateIPv4('192.168.1.1', 16);
    assertEqual(result.isPrivate, true);
});

test('IPv4: 8.8.8.8 is not private', () => {
    const result = SubnetCalculator.calculateIPv4('8.8.8.8', 32);
    assertEqual(result.isPrivate, false);
});

console.log('\n--- IPv4 Mask Input ---\n');

test('IPv4: Accept subnet mask as string', () => {
    const result = SubnetCalculator.calculateIPv4('192.168.1.100', '255.255.255.0');
    assertEqual(result.cidr, 24);
    assertEqual(result.networkAddress, '192.168.1.0');
});

// ============================================
// IPv6 Tests
// ============================================

console.log('\n--- IPv6 Expansion/Compression ---\n');

test('IPv6: Expand abbreviated address', () => {
    const expanded = SubnetCalculator.expandIPv6('2001:db8::1');
    assertEqual(expanded, '2001:0db8:0000:0000:0000:0000:0000:0001');
});

test('IPv6: Expand leading zeros', () => {
    const expanded = SubnetCalculator.expandIPv6('2001:db8:85a3::8a2e:370:7334');
    assertEqual(expanded, '2001:0db8:85a3:0000:0000:8a2e:0370:7334');
});

test('IPv6: Compress address', () => {
    const compressed = SubnetCalculator.compressIPv6('2001:0db8:0000:0000:0000:0000:0000:0001');
    assertEqual(compressed, '2001:db8::1');
});

test('IPv6: Compress all zeros', () => {
    const compressed = SubnetCalculator.compressIPv6('0000:0000:0000:0000:0000:0000:0000:0000');
    assertEqual(compressed, '::');
});

console.log('\n--- IPv6 Subnet Calculation ---\n');

test('IPv6: 2001:db8::1/64 network address', () => {
    const result = SubnetCalculator.calculateIPv6('2001:db8::1', 64);
    assertEqual(result.networkAddress, '2001:db8::');
});

test('IPv6: 2001:db8::1/64 last address', () => {
    const result = SubnetCalculator.calculateIPv6('2001:db8::1', 64);
    assertEqual(result.lastAddress, '2001:db8::ffff:ffff:ffff:ffff');
});

test('IPv6: 2001:db8::/32 total addresses', () => {
    const result = SubnetCalculator.calculateIPv6('2001:db8::', 32);
    // 2^96 addresses
    assertEqual(result.totalAddresses, '79228162514264337593543950336');
});

console.log('\n--- IPv6 Address Types ---\n');

test('IPv6: Global Unicast', () => {
    const result = SubnetCalculator.calculateIPv6('2001:db8::1', 64);
    assertEqual(result.addressType, 'Global Unicast');
});

test('IPv6: Link-Local', () => {
    const result = SubnetCalculator.calculateIPv6('fe80::1', 64);
    assertEqual(result.addressType, 'Link-Local');
});

test('IPv6: Loopback', () => {
    const result = SubnetCalculator.calculateIPv6('::1', 128);
    assertEqual(result.addressType, 'Loopback');
});

// ============================================
// Validation Tests
// ============================================

console.log('\n--- Validation Tests ---\n');

test('isValidIPv4: valid address', () => {
    assertEqual(SubnetCalculator.isValidIPv4('192.168.1.1'), true);
});

test('isValidIPv4: invalid (too many octets)', () => {
    assertEqual(SubnetCalculator.isValidIPv4('192.168.1.1.1'), false);
});

test('isValidIPv4: invalid (octet > 255)', () => {
    assertEqual(SubnetCalculator.isValidIPv4('192.168.1.256'), false);
});

test('isValidIPv6: valid address', () => {
    assertEqual(SubnetCalculator.isValidIPv6('2001:db8::1'), true);
});

test('isValidIPv6: valid full address', () => {
    assertEqual(SubnetCalculator.isValidIPv6('2001:0db8:85a3:0000:0000:8a2e:0370:7334'), true);
});

// ============================================
// Helper Function Tests
// ============================================

console.log('\n--- Helper Functions ---\n');

test('ipv4ToInt and intToIpv4 roundtrip', () => {
    const ip = '192.168.1.100';
    const int = SubnetCalculator.ipv4ToInt(ip);
    const back = SubnetCalculator.intToIpv4(int);
    assertEqual(back, ip);
});

test('cidrToMask: /24', () => {
    const mask = SubnetCalculator.cidrToMask(24);
    assertEqual(SubnetCalculator.intToIpv4(mask), '255.255.255.0');
});

test('cidrToMask: /16', () => {
    const mask = SubnetCalculator.cidrToMask(16);
    assertEqual(SubnetCalculator.intToIpv4(mask), '255.255.0.0');
});

test('maskToCidr: 255.255.255.0', () => {
    const cidr = SubnetCalculator.maskToCidr(SubnetCalculator.ipv4ToInt('255.255.255.0'));
    assertEqual(cidr, 24);
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
