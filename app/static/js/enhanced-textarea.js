/**
 * Enhanced Textarea Component
 * Adds cursor position, line number, and selection count display to textareas
 */

class EnhancedTextarea {
    constructor(textareaId) {
        this.textarea = document.getElementById(textareaId);
        if (!this.textarea) {
            console.error(`Textarea with id "${textareaId}" not found`);
            return;
        }
        
        this.init();
    }
    
    init() {
        // Create status bar
        this.statusBar = document.createElement('div');
        this.statusBar.className = 'enhanced-textarea-status';
        
        // Insert status bar after textarea
        this.textarea.parentNode.insertBefore(this.statusBar, this.textarea.nextSibling);
        
        // Add event listeners
        this.textarea.addEventListener('input', () => this.updateStatus());
        this.textarea.addEventListener('click', () => this.updateStatus());
        this.textarea.addEventListener('keyup', () => this.updateStatus());
        this.textarea.addEventListener('select', () => this.updateStatus());
        this.textarea.addEventListener('mouseup', () => this.updateStatus());
        
        // Initial update
        this.updateStatus();
    }
    
    updateStatus() {
        const text = this.textarea.value;
        const cursorPos = this.textarea.selectionStart;
        const selectionLength = this.textarea.selectionEnd - this.textarea.selectionStart;
        
        // Calculate line number
        const textBeforeCursor = text.substring(0, cursorPos);
        const lineNumber = textBeforeCursor.split('\n').length;
        const totalLines = text.split('\n').length;
        
        // Build status text
        let statusParts = [];
        
        // Cursor position
        statusParts.push(`Pos: ${cursorPos}/${text.length}`);
        
        // Line number
        statusParts.push(`Line: ${lineNumber}/${totalLines}`);
        
        // Selection count (if any)
        if (selectionLength > 0) {
            statusParts.push(`Selected: ${selectionLength}`);
        }
        
        this.statusBar.textContent = statusParts.join(' | ');
    }
}

// Auto-initialize all textareas with data-enhanced attribute
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('textarea[data-enhanced]').forEach(textarea => {
        new EnhancedTextarea(textarea.id);
    });
});
