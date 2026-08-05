/**
 * GiroCode / EPC QR Code Library
 * Builds the payload string for a SEPA Credit Transfer (SCT) EPC QR Code
 * according to EPC069-12 (version 002).
 *
 * Reuses the shared IbanValidator library for IBAN validation.
 * Works in both browser and Node.js environments.
 */

(function(root, factory) {
    if (typeof module === 'object' && module.exports) {
        // Node.js
        module.exports = factory(require('./iban_validator.js'));
    } else {
        // Browser
        root.GiroCode = factory(root.IbanValidator);
    }
}(typeof self !== 'undefined' ? self : this, function(IbanValidator) {
    'use strict';

    // Field length limits per EPC069-12
    const MAX_NAME = 70;
    const MAX_PURPOSE = 4;
    const MAX_REMITTANCE = 140;
    const MAX_PAYLOAD_BYTES = 331;

    // Amount bounds (EUR)
    const MIN_AMOUNT = 0.01;
    const MAX_AMOUNT = 999999999.99;

    /**
     * Number of UTF-8 bytes in a string.
     * @param {string} str
     * @returns {number}
     */
    function byteLength(str) {
        if (typeof TextEncoder !== 'undefined') {
            return new TextEncoder().encode(str).length;
        }
        // Node.js fallback
        return Buffer.byteLength(str, 'utf8');
    }

    /**
     * Normalize and format an amount into the EPC "EUR<value>" representation.
     * Accepts numbers or strings using either '.' or ',' as decimal separator.
     * @param {string|number} amount
     * @returns {{value: string|null, error: string|null}}
     */
    function formatAmount(amount) {
        if (amount === null || amount === undefined || amount === '') {
            return { value: null, error: null };
        }

        let raw = String(amount).trim();
        if (raw === '') {
            return { value: null, error: null };
        }

        // Support German-style decimal comma and thousands separators.
        // Strip spaces first, then normalize separators.
        raw = raw.replace(/\s/g, '');
        if (raw.indexOf(',') !== -1 && raw.indexOf('.') !== -1) {
            // Assume '.' is thousands separator, ',' is decimal (e.g. 1.234,56)
            raw = raw.replace(/\./g, '').replace(',', '.');
        } else {
            raw = raw.replace(',', '.');
        }

        if (!/^\d+(\.\d+)?$/.test(raw)) {
            return { value: null, error: 'Invalid amount' };
        }

        const num = parseFloat(raw);
        if (isNaN(num)) {
            return { value: null, error: 'Invalid amount' };
        }
        if (num < MIN_AMOUNT) {
            return { value: null, error: 'Amount must be at least 0.01 EUR' };
        }
        if (num > MAX_AMOUNT) {
            return { value: null, error: 'Amount must not exceed 999999999.99 EUR' };
        }

        // EPC amount: 'EUR' + value with a dot and exactly 2 decimals
        return { value: 'EUR' + num.toFixed(2), error: null };
    }

    /**
     * Validate a BIC (8 or 11 characters, letters/digits).
     * @param {string} bic
     * @returns {boolean}
     */
    function isValidBic(bic) {
        return /^[A-Z0-9]{8}([A-Z0-9]{3})?$/.test(bic);
    }

    /**
     * Build and validate an EPC (GiroCode) payload.
     *
     * @param {Object} data
     * @param {string} data.name       - Beneficiary / account holder name (required, 1..70)
     * @param {string} data.iban       - Beneficiary IBAN (required, validated)
     * @param {string} [data.bic]      - BIC (optional, 8 or 11 chars)
     * @param {string|number} [data.amount]    - Amount in EUR (optional)
     * @param {string} [data.purpose]  - Purpose code (optional, max 4)
     * @param {string} [data.reference]- Unstructured remittance / Verwendungszweck (optional, max 140)
     * @param {string} [data.version]  - '001' or '002' (default '002')
     * @returns {{valid: boolean, errors: string[], payload: string|null}}
     */
    function build(data) {
        data = data || {};
        const errors = [];

        const version = data.version === '001' ? '001' : '002';
        const name = (data.name || '').trim();
        const iban = IbanValidator ? IbanValidator.cleanIban(data.iban || '') : String(data.iban || '').replace(/\s/g, '').toUpperCase();
        const bic = (data.bic || '').replace(/\s/g, '').toUpperCase();
        const purpose = (data.purpose || '').trim();
        const reference = (data.reference || '').trim();

        // Name (mandatory)
        if (!name) {
            errors.push('Name is required');
        } else if (name.length > MAX_NAME) {
            errors.push('Name must not exceed ' + MAX_NAME + ' characters');
        }

        // IBAN (mandatory)
        if (!iban) {
            errors.push('IBAN is required');
        } else if (IbanValidator) {
            const ibanResult = IbanValidator.validate(iban);
            if (!ibanResult.valid) {
                errors.push('Invalid IBAN: ' + (ibanResult.errors[0] || 'unknown error'));
            }
        }

        // BIC (optional in v002, mandatory in v001)
        if (bic) {
            if (!isValidBic(bic)) {
                errors.push('Invalid BIC (must be 8 or 11 alphanumeric characters)');
            }
        } else if (version === '001') {
            errors.push('BIC is required for version 001');
        }

        // Amount (optional)
        const amountResult = formatAmount(data.amount);
        if (amountResult.error) {
            errors.push(amountResult.error);
        }

        // Purpose (optional)
        if (purpose && purpose.length > MAX_PURPOSE) {
            errors.push('Purpose must not exceed ' + MAX_PURPOSE + ' characters');
        }

        // Remittance / Verwendungszweck (optional)
        if (reference && reference.length > MAX_REMITTANCE) {
            errors.push('Reference must not exceed ' + MAX_REMITTANCE + ' characters');
        }

        if (errors.length > 0) {
            return { valid: false, errors: errors, payload: null };
        }

        // Assemble payload lines (EPC069-12 field order).
        // Structured remittance (line 10) is left empty; the Verwendungszweck
        // is placed in the unstructured remittance field (line 11).
        const lines = [
            'BCD',                       // Service Tag
            version,                     // Version
            '1',                         // Character set: 1 = UTF-8
            'SCT',                       // Identification: SEPA Credit Transfer
            bic,                         // BIC (may be empty for v002)
            name,                        // Beneficiary name
            iban,                        // Beneficiary IBAN
            amountResult.value || '',    // Amount (EUR..)
            purpose,                     // Purpose
            '',                          // Structured remittance
            reference                    // Unstructured remittance (Verwendungszweck)
        ];

        const payload = lines.join('\n');

        if (byteLength(payload) > MAX_PAYLOAD_BYTES) {
            return {
                valid: false,
                errors: ['Payload exceeds ' + MAX_PAYLOAD_BYTES + ' bytes; shorten the reference or name'],
                payload: null
            };
        }

        return { valid: true, errors: [], payload: payload };
    }

    // Public API
    return {
        MAX_NAME: MAX_NAME,
        MAX_PURPOSE: MAX_PURPOSE,
        MAX_REMITTANCE: MAX_REMITTANCE,
        MAX_PAYLOAD_BYTES: MAX_PAYLOAD_BYTES,
        formatAmount: formatAmount,
        isValidBic: isValidBic,
        byteLength: byteLength,
        build: build
    };
}));
