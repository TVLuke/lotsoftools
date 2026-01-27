/**
 * Enhanced Textarea Component
 * Adds cursor position, line number, selection count display, and configurable controls to textareas
 * 
 * Usage:
 *   <textarea data-enhanced data-controls="syntax,transform">
 * 
 * Available controls:
 *   - syntax: Syntax highlighting (requires highlight.js)
 *   - transform: Text transformation dropdown (lowercase, uppercase, sort, etc.)
 * 
 * If no data-controls specified, all controls are available by default.
 * Set data-controls="" to disable all controls.
 */

class EnhancedTextarea {
    static AVAILABLE_CONTROLS = ['syntax', 'transform'];
    
    constructor(textareaId) {
        this.textarea = document.getElementById(textareaId);
        if (!this.textarea) {
            console.error(`Textarea with id "${textareaId}" not found`);
            return;
        }
        
        this.id = textareaId;
        this.controlsExpanded = false;
        this.syntaxEnabled = false;
        this.detectedLanguage = null;
        
        // History system
        this.history = [];
        this.historyIndex = -1;
        this.historyMax = 100;
        this.lastSavedValue = '';
        this.isNavigatingHistory = false;
        
        // Parse enabled controls from data attribute
        this.enabledControls = this.parseControls();
        
        this.init();
    }
    
    parseControls() {
        const controlsAttr = this.textarea.dataset.controls;
        
        // If attribute not present, enable all controls by default
        if (controlsAttr === undefined) {
            return [...EnhancedTextarea.AVAILABLE_CONTROLS];
        }
        
        // If empty string, no controls
        if (controlsAttr === '') {
            return [];
        }
        
        // Parse comma-separated list
        return controlsAttr.split(',').map(c => c.trim().toLowerCase()).filter(c => 
            EnhancedTextarea.AVAILABLE_CONTROLS.includes(c)
        );
    }
    
    hasControl(name) {
        return this.enabledControls.includes(name);
    }
    
    init() {
        // Create wrapper for status bar
        this.statusBar = document.createElement('div');
        this.statusBar.className = 'enhanced-textarea-status';
        
        // Create main status row (always visible)
        this.statusRow = document.createElement('div');
        this.statusRow.className = 'enhanced-textarea-status-row';
        
        // Status text (left side)
        this.statusText = document.createElement('span');
        this.statusText.className = 'enhanced-textarea-status-text';
        this.statusRow.appendChild(this.statusText);
        
        // Controls toggle button (right side) - only if there are controls
        if (this.enabledControls.length > 0) {
            this.toggleBtn = document.createElement('button');
            this.toggleBtn.type = 'button';
            this.toggleBtn.className = 'enhanced-textarea-toggle-btn';
            this.toggleBtn.innerHTML = '<i class="fas fa-cog"></i>';
            this.toggleBtn.title = 'Toggle controls';
            this.toggleBtn.addEventListener('click', () => this.toggleControls());
            this.statusRow.appendChild(this.toggleBtn);
        }
        
        this.statusBar.appendChild(this.statusRow);
        
        // Create controls panel (collapsible)
        if (this.enabledControls.length > 0) {
            this.controlsPanel = document.createElement('div');
            this.controlsPanel.className = 'enhanced-textarea-controls';
            this.controlsPanel.style.display = 'none';
            this.statusBar.appendChild(this.controlsPanel);
        }
        
        // Save original parent before any wrapping
        const originalParent = this.textarea.parentNode;
        const nextSibling = this.textarea.nextSibling;
        
        // Build controls (may wrap textarea)
        if (this.enabledControls.length > 0) {
            this.buildControls();
        }
        
        // Create history navigation arrows (top right of textarea)
        this.createHistoryNav();
        
        // Insert status bar after textarea (or wrapper if created)
        const insertAfter = this.syntaxWrapper || this.textarea;
        originalParent.insertBefore(this.statusBar, insertAfter.nextSibling);
        
        // Add event listeners
        this.textarea.addEventListener('input', () => this.updateStatus());
        this.textarea.addEventListener('click', () => this.updateStatus());
        this.textarea.addEventListener('keyup', () => this.updateStatus());
        this.textarea.addEventListener('select', () => this.updateStatus());
        this.textarea.addEventListener('mouseup', () => this.updateStatus());
        
        // History event listeners
        this.textarea.addEventListener('paste', () => {
            // Save state before paste
            this.saveToHistory();
            // Save state after paste (next tick)
            setTimeout(() => this.saveToHistory(), 0);
        });
        
        this.textarea.addEventListener('blur', () => {
            // Save state when focus is lost (if changed)
            this.saveToHistory();
        });
        
        // Initial update and save initial state
        this.updateStatus();
        this.saveToHistory();
    }
    
    createHistoryNav() {
        // Create container for history arrows
        this.historyNav = document.createElement('div');
        this.historyNav.className = 'enhanced-textarea-history-nav';
        
        // Back button
        this.historyBackBtn = document.createElement('button');
        this.historyBackBtn.type = 'button';
        this.historyBackBtn.className = 'enhanced-textarea-history-btn';
        this.historyBackBtn.innerHTML = '<i class="fas fa-arrow-left"></i>';
        this.historyBackBtn.title = 'Undo (history back)';
        this.historyBackBtn.disabled = true;
        this.historyBackBtn.addEventListener('click', () => this.historyBack());
        
        // Forward button
        this.historyForwardBtn = document.createElement('button');
        this.historyForwardBtn.type = 'button';
        this.historyForwardBtn.className = 'enhanced-textarea-history-btn';
        this.historyForwardBtn.innerHTML = '<i class="fas fa-arrow-right"></i>';
        this.historyForwardBtn.title = 'Redo (history forward)';
        this.historyForwardBtn.disabled = true;
        this.historyForwardBtn.addEventListener('click', () => this.historyForward());
        
        this.historyNav.appendChild(this.historyBackBtn);
        this.historyNav.appendChild(this.historyForwardBtn);
        
        // Insert into textarea's parent (wrapper or original parent)
        const parent = this.syntaxWrapper || this.textarea.parentNode;
        parent.style.position = 'relative';
        parent.appendChild(this.historyNav);
    }
    
    saveToHistory() {
        const currentValue = this.textarea.value;
        
        // Don't save if value hasn't changed
        if (currentValue === this.lastSavedValue) {
            return;
        }
        
        // Don't save while navigating history
        if (this.isNavigatingHistory) {
            return;
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
        
        this.updateHistoryButtons();
    }
    
    historyBack() {
        if (this.historyIndex <= 0) {
            return;
        }
        
        // Save current state first if it's different
        if (this.textarea.value !== this.lastSavedValue) {
            this.saveToHistory();
        }
        
        this.isNavigatingHistory = true;
        this.historyIndex--;
        this.textarea.value = this.history[this.historyIndex];
        this.lastSavedValue = this.history[this.historyIndex];
        this.isNavigatingHistory = false;
        
        this.textarea.dispatchEvent(new Event('input', { bubbles: true }));
        this.updateHistoryButtons();
        this.updateStatus();
    }
    
    historyForward() {
        if (this.historyIndex >= this.history.length - 1) {
            return;
        }
        
        this.isNavigatingHistory = true;
        this.historyIndex++;
        this.textarea.value = this.history[this.historyIndex];
        this.lastSavedValue = this.history[this.historyIndex];
        this.isNavigatingHistory = false;
        
        this.textarea.dispatchEvent(new Event('input', { bubbles: true }));
        this.updateHistoryButtons();
        this.updateStatus();
    }
    
    updateHistoryButtons() {
        if (this.historyBackBtn) {
            this.historyBackBtn.disabled = this.historyIndex <= 0;
        }
        if (this.historyForwardBtn) {
            this.historyForwardBtn.disabled = this.historyIndex >= this.history.length - 1;
        }
    }
    
    buildControls() {
        // Syntax highlighting control
        if (this.hasControl('syntax')) {
            const syntaxControl = document.createElement('div');
            syntaxControl.className = 'enhanced-textarea-control';
            
            const syntaxToggle = document.createElement('label');
            syntaxToggle.className = 'enhanced-textarea-control-label';
            
            const syntaxCheckbox = document.createElement('input');
            syntaxCheckbox.type = 'checkbox';
            syntaxCheckbox.id = `${this.id}-syntax-toggle`;
            syntaxCheckbox.addEventListener('change', (e) => this.toggleSyntax(e.target.checked));
            this.syntaxCheckbox = syntaxCheckbox;
            
            syntaxToggle.appendChild(syntaxCheckbox);
            syntaxToggle.appendChild(document.createTextNode(' Syntax highlighting'));
            
            // Language selector
            this.langSelect = document.createElement('select');
            this.langSelect.className = 'enhanced-textarea-lang-select';
            this.langSelect.innerHTML = `
                <option value="auto">Auto-detect</option>
                <option value="plaintext">Plain Text</option>
                <option value="javascript">JavaScript</option>
                <option value="python">Python</option>
                <option value="java">Java</option>
                <option value="css">CSS</option>
                <option value="html">HTML</option>
                <option value="xml">XML</option>
                <option value="json">JSON</option>
                <option value="yaml">YAML</option>
                <option value="markdown">Markdown</option>
                <option value="sql">SQL</option>
                <option value="bash">Bash</option>
                <option value="php">PHP</option>
                <option value="ruby">Ruby</option>
                <option value="go">Go</option>
                <option value="rust">Rust</option>
                <option value="typescript">TypeScript</option>
                <option value="c">C</option>
                <option value="cpp">C++</option>
                <option value="csharp">C#</option>
            `;
            this.langSelect.addEventListener('change', () => this.updateSyntaxHighlight());
            
            // Detected language display
            this.detectedLangSpan = document.createElement('span');
            this.detectedLangSpan.className = 'enhanced-textarea-detected-lang';
            
            syntaxControl.appendChild(syntaxToggle);
            syntaxControl.appendChild(this.langSelect);
            syntaxControl.appendChild(this.detectedLangSpan);
            
            this.controlsPanel.appendChild(syntaxControl);
            
            // Create syntax highlight overlay (initially hidden)
            this.createSyntaxOverlay();
        }
        
        // Text transform control
        if (this.hasControl('transform')) {
            const transformControl = document.createElement('div');
            transformControl.className = 'enhanced-textarea-control';
            
            const transformLabel = document.createElement('span');
            transformLabel.className = 'enhanced-textarea-control-label';
            transformLabel.textContent = 'Transform:';
            
            this.transformSelect = document.createElement('select');
            this.transformSelect.className = 'enhanced-textarea-transform-select';
            this.transformSelect.innerHTML = `
                <option value="">-- Select --</option>
                <option value="lowercase">Lowercase / Alles klein</option>
                <option value="uppercase">Uppercase / Alles groß</option>
                <option value="sortlines">Sort lines / Zeilen sortieren</option>
                <option value="linebreaks-to-spaces">Linebreaks → Spaces</option>
                <option value="trim">Trim whitespace</option>
                <option value="remove-whitespace">Remove all whitespace</option>
            `;
            this.transformSelect.addEventListener('change', (e) => {
                if (e.target.value) {
                    this.applyTransform(e.target.value);
                    e.target.value = ''; // Reset dropdown
                }
            });
            
            transformControl.appendChild(transformLabel);
            transformControl.appendChild(this.transformSelect);
            
            this.controlsPanel.appendChild(transformControl);
        }
    }
    
    applyTransform(type) {
        // Save state before transformation
        this.saveToHistory();
        
        const text = this.textarea.value;
        let transformed;
        
        switch (type) {
            case 'lowercase':
                transformed = text.toLowerCase();
                break;
            case 'uppercase':
                transformed = text.toUpperCase();
                break;
            case 'sortlines':
                transformed = text.split('\n').sort((a, b) => a.localeCompare(b)).join('\n');
                break;
            case 'linebreaks-to-spaces':
                transformed = text.replace(/\r?\n/g, ' ');
                break;
            case 'trim':
                transformed = text.trim();
                break;
            case 'remove-whitespace':
                transformed = text.replace(/\s+/g, '');
                break;
            default:
                return;
        }
        
        this.textarea.value = transformed;
        this.textarea.dispatchEvent(new Event('input', { bubbles: true }));
        
        // Save state after transformation
        this.saveToHistory();
        this.updateStatus();
    }
    
    createSyntaxOverlay() {
        // Wrap textarea in a container for proper overlay positioning
        this.syntaxWrapper = document.createElement('div');
        this.syntaxWrapper.className = 'enhanced-textarea-syntax-wrapper';
        this.textarea.parentNode.insertBefore(this.syntaxWrapper, this.textarea);
        this.syntaxWrapper.appendChild(this.textarea);
        
        // Create overlay container that sits behind the textarea
        this.syntaxOverlay = document.createElement('div');
        this.syntaxOverlay.className = 'enhanced-textarea-syntax-overlay';
        this.syntaxOverlay.style.display = 'none';
        
        this.syntaxPre = document.createElement('pre');
        this.syntaxCode = document.createElement('code');
        this.syntaxPre.appendChild(this.syntaxCode);
        this.syntaxOverlay.appendChild(this.syntaxPre);
        
        // Insert overlay before textarea within the wrapper
        this.syntaxWrapper.insertBefore(this.syntaxOverlay, this.textarea);
        
        // Sync scroll
        this.textarea.addEventListener('scroll', () => {
            if (this.syntaxEnabled) {
                this.syntaxPre.style.transform = `translate(-${this.textarea.scrollLeft}px, -${this.textarea.scrollTop}px)`;
            }
        });
        
        // Sync dimensions on resize
        if (typeof ResizeObserver !== 'undefined') {
            this.resizeObserver = new ResizeObserver(() => {
                if (this.syntaxEnabled) {
                    this.syncOverlayDimensions();
                }
            });
            this.resizeObserver.observe(this.textarea);
        }
    }
    
    toggleControls() {
        this.controlsExpanded = !this.controlsExpanded;
        this.controlsPanel.style.display = this.controlsExpanded ? 'block' : 'none';
        this.toggleBtn.classList.toggle('active', this.controlsExpanded);
    }
    
    toggleSyntax(enabled) {
        this.syntaxEnabled = enabled;
        
        if (enabled) {
            this.textarea.classList.add('syntax-active');
            this.syntaxOverlay.style.display = 'block';
            this.updateSyntaxHighlight();
        } else {
            this.textarea.classList.remove('syntax-active');
            this.syntaxOverlay.style.display = 'none';
        }
    }
    
    updateSyntaxHighlight() {
        if (!this.syntaxEnabled || typeof hljs === 'undefined') {
            if (this.syntaxEnabled && typeof hljs === 'undefined') {
                console.warn('highlight.js not loaded. Include the highlightjs import component.');
            }
            return;
        }
        
        const text = this.textarea.value;
        const selectedLang = this.langSelect.value;
        
        // Add newline to prevent collapsing empty last line
        let codeText = text;
        if (text.endsWith('\n') || text === '') {
            codeText = text + ' ';
        }
        
        this.syntaxCode.textContent = codeText;
        
        if (selectedLang === 'auto') {
            // Auto-detect language
            const result = hljs.highlightAuto(codeText);
            this.syntaxCode.innerHTML = result.value;
            this.detectedLanguage = result.language || 'plaintext';
            this.detectedLangSpan.textContent = `(${this.detectedLanguage})`;
        } else if (selectedLang === 'plaintext') {
            this.syntaxCode.textContent = codeText;
            this.detectedLanguage = 'plaintext';
            this.detectedLangSpan.textContent = '';
        } else {
            // Highlight with selected language
            const result = hljs.highlight(codeText, { language: selectedLang, ignoreIllegals: true });
            this.syntaxCode.innerHTML = result.value;
            this.detectedLanguage = selectedLang;
            this.detectedLangSpan.textContent = '';
        }
        
        // Sync dimensions
        this.syncOverlayDimensions();
    }
    
    syncOverlayDimensions() {
        if (!this.syntaxOverlay) return;
        
        const styles = window.getComputedStyle(this.textarea);
        const rect = this.textarea.getBoundingClientRect();
        
        // Match textarea dimensions exactly
        this.syntaxOverlay.style.width = rect.width + 'px';
        this.syntaxOverlay.style.height = rect.height + 'px';
        
        // Match typography
        this.syntaxPre.style.padding = styles.padding;
        this.syntaxPre.style.fontSize = styles.fontSize;
        this.syntaxPre.style.fontFamily = styles.fontFamily;
        this.syntaxPre.style.lineHeight = styles.lineHeight;
        this.syntaxPre.style.letterSpacing = styles.letterSpacing;
        this.syntaxPre.style.wordSpacing = styles.wordSpacing;
        this.syntaxPre.style.tabSize = styles.tabSize;
        
        // Sync current scroll position
        this.syntaxPre.style.transform = `translate(-${this.textarea.scrollLeft}px, -${this.textarea.scrollTop}px)`;
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
        
        this.statusText.textContent = statusParts.join(' | ');
        
        // Update syntax highlighting if enabled
        if (this.syntaxEnabled) {
            this.updateSyntaxHighlight();
        }
    }
}

// Auto-initialize all textareas with data-enhanced attribute
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('textarea[data-enhanced]').forEach(textarea => {
        new EnhancedTextarea(textarea.id);
    });
});
