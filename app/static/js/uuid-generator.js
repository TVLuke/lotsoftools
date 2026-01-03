/**
 * Native UUID Generation Functions
 * No external dependencies required
 */

// UUID v4 - Random
function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// UUID v1 - Timestamp-based with random node
function uuidv1() {
    const now = Date.now();
    const nsecs = ((now * 10000) + 122192928000000000) % 0x100000000;
    
    const timeLow = (nsecs & 0xffffffff).toString(16).padStart(8, '0');
    const timeMid = ((nsecs / 0x100000000) & 0xffff).toString(16).padStart(4, '0');
    const timeHi = (((nsecs / 0x1000000000000) & 0x0fff) | 0x1000).toString(16).padStart(4, '0');
    
    const clockSeq = (Math.random() * 0x3fff | 0x8000).toString(16).padStart(4, '0');
    const node = Array.from({length: 6}, () => Math.floor(Math.random() * 256).toString(16).padStart(2, '0')).join('');
    
    return `${timeLow}-${timeMid}-${timeHi}-${clockSeq}-${node}`;
}

// UUID v7 - Timestamp-ordered (recommended for databases)
function uuidv7() {
    const timestamp = Date.now();
    
    // 48-bit timestamp in milliseconds
    const timestampHex = timestamp.toString(16).padStart(12, '0');
    
    // 12-bit random sequence
    const seq = Math.floor(Math.random() * 0xfff).toString(16).padStart(3, '0');
    
    // 62-bit random data
    const rand = Array.from({length: 15}, () => 
        Math.floor(Math.random() * 16).toString(16)
    ).join('');
    
    // Format: tttttttt-tttt-7xxx-yxxx-xxxxxxxxxxxx
    return `${timestampHex.slice(0, 8)}-${timestampHex.slice(8, 12)}-7${seq}-${(Math.random() * 16 | 0x8).toString(16)}${rand.slice(0, 3)}-${rand.slice(3)}`;
}

// Export as uuid object for compatibility
window.uuid = {
    v1: uuidv1,
    v4: uuidv4,
    v7: uuidv7
};
