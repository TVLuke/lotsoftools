/**
 * Subnet Calculator Library
 * Supports IPv4 and IPv6 subnet calculations
 */

const SubnetCalculator = (function() {
    'use strict';

    // ============================================
    // IPv4 Functions
    // ============================================

    /**
     * Parse IPv4 address string to 32-bit integer
     */
    function ipv4ToInt(ip) {
        const parts = ip.split('.');
        if (parts.length !== 4) throw new Error('Invalid IPv4 address');
        
        let result = 0;
        for (let i = 0; i < 4; i++) {
            const octet = parseInt(parts[i], 10);
            if (isNaN(octet) || octet < 0 || octet > 255) {
                throw new Error('Invalid IPv4 octet: ' + parts[i]);
            }
            result = (result << 8) + octet;
        }
        return result >>> 0; // Convert to unsigned
    }

    /**
     * Convert 32-bit integer to IPv4 address string
     */
    function intToIpv4(num) {
        return [
            (num >>> 24) & 255,
            (num >>> 16) & 255,
            (num >>> 8) & 255,
            num & 255
        ].join('.');
    }

    /**
     * Create subnet mask from CIDR prefix length
     */
    function cidrToMask(cidr) {
        if (cidr < 0 || cidr > 32) throw new Error('Invalid CIDR (must be 0-32)');
        if (cidr === 0) return 0;
        return (0xFFFFFFFF << (32 - cidr)) >>> 0;
    }

    /**
     * Convert subnet mask to CIDR prefix length
     */
    function maskToCidr(mask) {
        let cidr = 0;
        let m = mask >>> 0;
        while (m & 0x80000000) {
            cidr++;
            m = (m << 1) >>> 0;
        }
        return cidr;
    }

    /**
     * Calculate IPv4 subnet information
     */
    function calculateIPv4(ipAddress, cidrOrMask) {
        const ip = ipv4ToInt(ipAddress);
        
        let cidr, mask;
        if (typeof cidrOrMask === 'string' && cidrOrMask.includes('.')) {
            mask = ipv4ToInt(cidrOrMask);
            cidr = maskToCidr(mask);
        } else {
            cidr = parseInt(cidrOrMask, 10);
            mask = cidrToMask(cidr);
        }

        const network = (ip & mask) >>> 0;
        const broadcast = (network | (~mask >>> 0)) >>> 0;
        const hostMin = cidr < 31 ? network + 1 : network;
        const hostMax = cidr < 31 ? broadcast - 1 : broadcast;
        const totalHosts = Math.pow(2, 32 - cidr);
        const usableHosts = cidr <= 30 ? totalHosts - 2 : (cidr === 31 ? 2 : 1);
        const wildcard = (~mask) >>> 0;

        // Determine IP class
        let ipClass = 'N/A';
        const firstOctet = (ip >>> 24) & 255;
        if (firstOctet >= 1 && firstOctet <= 126) ipClass = 'A';
        else if (firstOctet >= 128 && firstOctet <= 191) ipClass = 'B';
        else if (firstOctet >= 192 && firstOctet <= 223) ipClass = 'C';
        else if (firstOctet >= 224 && firstOctet <= 239) ipClass = 'D (Multicast)';
        else if (firstOctet >= 240 && firstOctet <= 255) ipClass = 'E (Reserved)';

        // Check if private
        let isPrivate = false;
        if ((ip >>> 24) === 10) isPrivate = true; // 10.0.0.0/8
        else if ((ip >>> 20) === 0xAC1) isPrivate = true; // 172.16.0.0/12
        else if ((ip >>> 16) === 0xC0A8) isPrivate = true; // 192.168.0.0/16

        return {
            ipAddress: ipAddress,
            cidr: cidr,
            networkAddress: intToIpv4(network),
            broadcastAddress: intToIpv4(broadcast),
            subnetMask: intToIpv4(mask),
            wildcardMask: intToIpv4(wildcard),
            hostMin: intToIpv4(hostMin),
            hostMax: intToIpv4(hostMax),
            totalHosts: totalHosts,
            usableHosts: usableHosts,
            ipClass: ipClass,
            isPrivate: isPrivate,
            binary: {
                ip: intToBinary32(ip),
                mask: intToBinary32(mask),
                network: intToBinary32(network)
            }
        };
    }

    function intToBinary32(num) {
        return (num >>> 0).toString(2).padStart(32, '0').match(/.{8}/g).join('.');
    }

    // ============================================
    // IPv6 Functions
    // ============================================

    /**
     * Expand abbreviated IPv6 address to full form
     */
    function expandIPv6(ip) {
        // Handle :: abbreviation
        if (ip.includes('::')) {
            const parts = ip.split('::');
            const left = parts[0] ? parts[0].split(':') : [];
            const right = parts[1] ? parts[1].split(':') : [];
            const missing = 8 - left.length - right.length;
            const middle = Array(missing).fill('0000');
            const full = [...left, ...middle, ...right];
            return full.map(p => p.padStart(4, '0')).join(':');
        }
        return ip.split(':').map(p => p.padStart(4, '0')).join(':');
    }

    /**
     * Compress IPv6 address to shortest form
     */
    function compressIPv6(ip) {
        const expanded = expandIPv6(ip);
        let groups = expanded.split(':').map(g => g.replace(/^0+/, '') || '0');
        
        // Find longest run of zeros
        let maxStart = -1, maxLen = 0, currStart = -1, currLen = 0;
        for (let i = 0; i < 8; i++) {
            if (groups[i] === '0') {
                if (currStart === -1) currStart = i;
                currLen++;
                if (currLen > maxLen) {
                    maxLen = currLen;
                    maxStart = currStart;
                }
            } else {
                currStart = -1;
                currLen = 0;
            }
        }

        if (maxLen > 1) {
            const before = groups.slice(0, maxStart);
            const after = groups.slice(maxStart + maxLen);
            if (before.length === 0 && after.length === 0) return '::';
            if (before.length === 0) return '::' + after.join(':');
            if (after.length === 0) return before.join(':') + '::';
            return before.join(':') + '::' + after.join(':');
        }
        return groups.join(':');
    }

    /**
     * Parse IPv6 to array of 8 16-bit values
     */
    function ipv6ToArray(ip) {
        const expanded = expandIPv6(ip);
        return expanded.split(':').map(p => parseInt(p, 16));
    }

    /**
     * Convert array of 8 16-bit values to IPv6 string
     */
    function arrayToIpv6(arr) {
        return arr.map(n => n.toString(16).padStart(4, '0')).join(':');
    }

    /**
     * Calculate IPv6 subnet information
     */
    function calculateIPv6(ipAddress, prefix) {
        prefix = parseInt(prefix, 10);
        if (prefix < 0 || prefix > 128) throw new Error('Invalid prefix (must be 0-128)');

        const ipArr = ipv6ToArray(ipAddress);
        const expanded = expandIPv6(ipAddress);

        // Calculate network address
        const networkArr = [...ipArr];
        let bitsRemaining = prefix;
        for (let i = 0; i < 8; i++) {
            if (bitsRemaining >= 16) {
                bitsRemaining -= 16;
            } else if (bitsRemaining > 0) {
                const mask = (0xFFFF << (16 - bitsRemaining)) & 0xFFFF;
                networkArr[i] = ipArr[i] & mask;
                bitsRemaining = 0;
            } else {
                networkArr[i] = 0;
            }
        }

        // Calculate last address in range
        const lastArr = [...networkArr];
        bitsRemaining = prefix;
        for (let i = 0; i < 8; i++) {
            if (bitsRemaining >= 16) {
                bitsRemaining -= 16;
            } else if (bitsRemaining > 0) {
                const hostBits = 16 - bitsRemaining;
                lastArr[i] = networkArr[i] | ((1 << hostBits) - 1);
                bitsRemaining = 0;
            } else {
                lastArr[i] = 0xFFFF;
            }
        }

        const networkAddress = arrayToIpv6(networkArr);
        const lastAddress = arrayToIpv6(lastArr);
        
        // Total addresses (as BigInt for large numbers)
        const hostBits = 128 - prefix;
        let totalAddresses;
        if (hostBits <= 53) {
            totalAddresses = Math.pow(2, hostBits);
        } else {
            totalAddresses = BigInt(2) ** BigInt(hostBits);
        }

        // Determine address type
        let addressType = 'Global Unicast';
        if (expanded.startsWith('fe80')) addressType = 'Link-Local';
        else if (expanded.startsWith('fc') || expanded.startsWith('fd')) addressType = 'Unique Local';
        else if (expanded.startsWith('ff')) addressType = 'Multicast';
        else if (expanded === '0000:0000:0000:0000:0000:0000:0000:0001') addressType = 'Loopback';
        else if (expanded === '0000:0000:0000:0000:0000:0000:0000:0000') addressType = 'Unspecified';

        return {
            ipAddress: ipAddress,
            expanded: expanded,
            compressed: compressIPv6(ipAddress),
            prefix: prefix,
            networkAddress: compressIPv6(networkAddress),
            networkAddressFull: networkAddress,
            lastAddress: compressIPv6(lastAddress),
            lastAddressFull: lastAddress,
            totalAddresses: totalAddresses.toString(),
            addressType: addressType
        };
    }

    /**
     * Validate IPv4 address
     */
    function isValidIPv4(ip) {
        const parts = ip.split('.');
        if (parts.length !== 4) return false;
        return parts.every(p => {
            const num = parseInt(p, 10);
            return !isNaN(num) && num >= 0 && num <= 255 && p === num.toString();
        });
    }

    /**
     * Validate IPv6 address
     */
    function isValidIPv6(ip) {
        try {
            expandIPv6(ip);
            const parts = ip.replace('::', ':x:').split(':');
            if (parts.filter(p => p === 'x').length > 1) return false;
            return parts.every(p => p === 'x' || /^[0-9a-fA-F]{1,4}$/.test(p));
        } catch {
            return false;
        }
    }

    // Public API
    return {
        calculateIPv4: calculateIPv4,
        calculateIPv6: calculateIPv6,
        isValidIPv4: isValidIPv4,
        isValidIPv6: isValidIPv6,
        expandIPv6: expandIPv6,
        compressIPv6: compressIPv6,
        ipv4ToInt: ipv4ToInt,
        intToIpv4: intToIpv4,
        cidrToMask: cidrToMask,
        maskToCidr: maskToCidr
    };
})();

// Export for Node.js/testing environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SubnetCalculator;
}
