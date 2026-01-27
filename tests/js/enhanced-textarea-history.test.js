/**
 * Tests for Enhanced Textarea - History System
 * Run with: node enhanced-textarea-history.test.js
 * 
 * Tests the undo/redo history behavior, especially:
 * - Basic history recording
 * - Navigation back and forward
 * - Branch replacement: when going back and making changes,
 *   newer history entries are replaced (no branching)
 */

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

function assertEqual(actual, expected, message) {
    if (actual === expected) {
        passed++;
        console.log(`✓ ${message}`);
    } else {
        failed++;
        console.log(`✗ ${message}`);
        console.log(`  Expected: "${expected}"`);
        console.log(`  Actual:   "${actual}"`);
    }
}

function assertArrayEqual(actual, expected, message) {
    const actualStr = JSON.stringify(actual);
    const expectedStr = JSON.stringify(expected);
    if (actualStr === expectedStr) {
        passed++;
        console.log(`✓ ${message}`);
    } else {
        failed++;
        console.log(`✗ ${message}`);
        console.log(`  Expected: ${expectedStr}`);
        console.log(`  Actual:   ${actualStr}`);
    }
}

/**
 * Mock History Manager - mimics the history logic from EnhancedTextarea
 * This allows testing the history logic without DOM dependencies
 */
class MockHistoryManager {
    constructor(maxHistory = 100) {
        this.history = [];
        this.historyIndex = -1;
        this.historyMax = maxHistory;
        this.lastSavedValue = '';
        this.isNavigatingHistory = false;
        this.currentValue = '';
    }
    
    // Simulate setting textarea value
    setValue(value) {
        this.currentValue = value;
    }
    
    getValue() {
        return this.currentValue;
    }
    
    saveToHistory() {
        const currentValue = this.currentValue;
        
        // Don't save if value hasn't changed
        if (currentValue === this.lastSavedValue) {
            return false;
        }
        
        // Don't save while navigating history
        if (this.isNavigatingHistory) {
            return false;
        }
        
        // If we're not at the end of history, remove everything after current position
        if (this.historyIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.historyIndex + 1);
        }
        
        // Add new state
        this.history.push(currentValue);
        this.historyIndex = this.history.length - 1;
        this.lastSavedValue = currentValue;
        
        // Trim history if exceeds max
        if (this.history.length > this.historyMax) {
            this.history.shift();
            this.historyIndex--;
        }
        
        return true;
    }
    
    historyBack() {
        if (this.historyIndex <= 0) {
            return false;
        }
        
        // Save current state first if it's different
        if (this.currentValue !== this.lastSavedValue) {
            this.saveToHistory();
        }
        
        this.isNavigatingHistory = true;
        this.historyIndex--;
        this.currentValue = this.history[this.historyIndex];
        this.lastSavedValue = this.history[this.historyIndex];
        this.isNavigatingHistory = false;
        
        return true;
    }
    
    historyForward() {
        if (this.historyIndex >= this.history.length - 1) {
            return false;
        }
        
        this.isNavigatingHistory = true;
        this.historyIndex++;
        this.currentValue = this.history[this.historyIndex];
        this.lastSavedValue = this.history[this.historyIndex];
        this.isNavigatingHistory = false;
        
        return true;
    }
    
    canGoBack() {
        return this.historyIndex > 0;
    }
    
    canGoForward() {
        return this.historyIndex < this.history.length - 1;
    }
}

console.log('=== Enhanced Textarea History Tests ===\n');

// Test basic history recording
console.log('--- Basic History Recording ---');

let hm = new MockHistoryManager();
hm.setValue('step1');
hm.saveToHistory();
assertEqual(hm.history.length, 1, 'Step 1 saved');

hm.setValue('step2');
hm.saveToHistory();
assertEqual(hm.history.length, 2, 'Step 2 saved');

hm.setValue('step3');
hm.saveToHistory();
assertEqual(hm.history.length, 3, 'Step 3 saved');

assertArrayEqual(hm.history, ['step1', 'step2', 'step3'], 'History contains all steps in order');
assertEqual(hm.historyIndex, 2, 'History index at end');

// Test no duplicate saves
console.log('\n--- No Duplicate Saves ---');

hm = new MockHistoryManager();
hm.setValue('same');
hm.saveToHistory();
hm.saveToHistory(); // Same value
hm.saveToHistory(); // Same value again
assertEqual(hm.history.length, 1, 'Duplicate values not saved');

// Test navigation back
console.log('\n--- Navigation Back ---');

hm = new MockHistoryManager();
hm.setValue('step1');
hm.saveToHistory();
hm.setValue('step2');
hm.saveToHistory();
hm.setValue('step3');
hm.saveToHistory();

assert(hm.canGoBack(), 'Can go back from step3');
hm.historyBack();
assertEqual(hm.getValue(), 'step2', 'Back to step2');
assertEqual(hm.historyIndex, 1, 'Index at 1');

hm.historyBack();
assertEqual(hm.getValue(), 'step1', 'Back to step1');
assertEqual(hm.historyIndex, 0, 'Index at 0');

assert(!hm.canGoBack(), 'Cannot go back from first entry');
assert(!hm.historyBack(), 'historyBack returns false at beginning');

// Test navigation forward
console.log('\n--- Navigation Forward ---');

hm = new MockHistoryManager();
hm.setValue('step1');
hm.saveToHistory();
hm.setValue('step2');
hm.saveToHistory();
hm.setValue('step3');
hm.saveToHistory();

hm.historyBack();
hm.historyBack();
assertEqual(hm.getValue(), 'step1', 'Went back to step1');

assert(hm.canGoForward(), 'Can go forward from step1');
hm.historyForward();
assertEqual(hm.getValue(), 'step2', 'Forward to step2');

hm.historyForward();
assertEqual(hm.getValue(), 'step3', 'Forward to step3');

assert(!hm.canGoForward(), 'Cannot go forward from last entry');
assert(!hm.historyForward(), 'historyForward returns false at end');

// CRITICAL TEST: Branch replacement
console.log('\n--- Branch Replacement (Critical) ---');
console.log('Scenario: Make changes 1,2,3,4 -> go back to 2 -> make change 3a');
console.log('Expected: History is [1,2,3a], steps 3 and 4 are gone');

hm = new MockHistoryManager();
hm.setValue('initial');
hm.saveToHistory();
hm.setValue('step1');
hm.saveToHistory();
hm.setValue('step2');
hm.saveToHistory();
hm.setValue('step3');
hm.saveToHistory();
hm.setValue('step4');
hm.saveToHistory();

assertArrayEqual(hm.history, ['initial', 'step1', 'step2', 'step3', 'step4'], 'Initial history correct');
assertEqual(hm.historyIndex, 4, 'At step4 (index 4)');

// Go back to step2 (index 2)
hm.historyBack(); // now at step3
hm.historyBack(); // now at step2
assertEqual(hm.getValue(), 'step2', 'Navigated back to step2');
assertEqual(hm.historyIndex, 2, 'Index at 2');

// Make a new change (step3a)
hm.setValue('step3a');
hm.saveToHistory();

// Verify branch replacement
assertArrayEqual(hm.history, ['initial', 'step1', 'step2', 'step3a'], 'History replaced: step3 and step4 gone, step3a added');
assertEqual(hm.historyIndex, 3, 'Index now at 3 (end)');
assertEqual(hm.getValue(), 'step3a', 'Current value is step3a');
assert(!hm.canGoForward(), 'Cannot go forward (at end of new branch)');

// Verify we can still go back through the preserved history
hm.historyBack();
assertEqual(hm.getValue(), 'step2', 'Can go back to step2');
hm.historyBack();
assertEqual(hm.getValue(), 'step1', 'Can go back to step1');
hm.historyBack();
assertEqual(hm.getValue(), 'initial', 'Can go back to initial');

// Test another branch replacement scenario
console.log('\n--- Branch Replacement Scenario 2 ---');
console.log('Scenario: 5 steps -> back to step 1 -> new change');

hm = new MockHistoryManager();
hm.setValue('A');
hm.saveToHistory();
hm.setValue('B');
hm.saveToHistory();
hm.setValue('C');
hm.saveToHistory();
hm.setValue('D');
hm.saveToHistory();
hm.setValue('E');
hm.saveToHistory();

assertEqual(hm.history.length, 5, 'Started with 5 entries');

// Go all the way back to A (index 0)
hm.historyBack(); // D
hm.historyBack(); // C
hm.historyBack(); // B
hm.historyBack(); // A
assertEqual(hm.getValue(), 'A', 'At step A');
assertEqual(hm.historyIndex, 0, 'Index at 0');

// Make new change
hm.setValue('A-modified');
hm.saveToHistory();

assertArrayEqual(hm.history, ['A', 'A-modified'], 'Only A and A-modified remain');
assertEqual(hm.historyIndex, 1, 'Index at 1');

// Test max history limit
console.log('\n--- Max History Limit ---');

hm = new MockHistoryManager(5); // Max 5 entries
for (let i = 1; i <= 7; i++) {
    hm.setValue(`entry${i}`);
    hm.saveToHistory();
}

assertEqual(hm.history.length, 5, 'History trimmed to max 5');
assertArrayEqual(hm.history, ['entry3', 'entry4', 'entry5', 'entry6', 'entry7'], 'Oldest entries removed');
assertEqual(hm.historyIndex, 4, 'Index adjusted after trim');

// Test unsaved changes before navigation
console.log('\n--- Unsaved Changes Before Navigation ---');

hm = new MockHistoryManager();
hm.setValue('saved1');
hm.saveToHistory();
hm.setValue('saved2');
hm.saveToHistory();
hm.setValue('unsaved-change'); // Not saved yet

// Going back should save the current state first
hm.historyBack();
assertEqual(hm.history.length, 3, 'Unsaved change was saved before going back');
assert(hm.history.includes('unsaved-change'), 'Unsaved change is in history');

// Test empty to content transition
console.log('\n--- Empty to Content ---');

hm = new MockHistoryManager();
hm.setValue(''); // Empty is same as initial lastSavedValue, won't be saved
hm.saveToHistory();
assertEqual(hm.history.length, 0, 'Empty string not saved (matches initial state)');

hm.setValue('first content');
hm.saveToHistory();
assertEqual(hm.history.length, 1, 'First content saved');

hm.setValue('second content');
hm.saveToHistory();
assertEqual(hm.history.length, 2, 'Second content saved');

hm.historyBack();
assertEqual(hm.getValue(), 'first content', 'Can go back to first content');

// Summary
console.log('\n=== Test Summary ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log(`Total: ${passed + failed}`);

if (failed > 0) {
    console.log('\n⚠️  Some tests failed!');
}

process.exit(failed > 0 ? 1 : 0);
