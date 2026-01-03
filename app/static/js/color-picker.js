/**
 * Color Picker Component
 * Provides circular color picker with hex input synchronization
 */

class ColorPicker {
    constructor(element) {
        this.container = element;
        this.colorInput = element.querySelector('input[type="color"]');
        this.hexInput = element.querySelector('.hex-input, .csv-hex-input');
        this.circle = element.querySelector('.color-circle, .csv-color-circle');
        
        if (!this.colorInput || !this.hexInput || !this.circle) {
            console.error('ColorPicker: Missing required elements', element);
            return;
        }
        
        this.init();
    }
    
    init() {
        // Sync color picker to hex input
        this.colorInput.addEventListener('input', () => {
            const color = this.colorInput.value.toUpperCase();
            this.hexInput.value = color;
            this.circle.style.backgroundColor = color;
            this.triggerChange();
        });
        
        // Sync hex input to color picker
        this.hexInput.addEventListener('input', () => {
            let value = this.hexInput.value.toUpperCase();
            
            // Auto-add # if missing
            if (!value.startsWith('#')) {
                value = '#' + value;
            }
            this.hexInput.value = value;
            
            // Validate and update if valid hex
            if (/^#[0-9A-F]{6}$/.test(value)) {
                this.colorInput.value = value;
                this.circle.style.backgroundColor = value;
                this.triggerChange();
            }
        });
    }
    
    triggerChange() {
        // Dispatch custom event for external listeners
        const event = new CustomEvent('colorchange', {
            detail: { color: this.colorInput.value },
            bubbles: true
        });
        this.container.dispatchEvent(event);
    }
    
    getValue() {
        return this.colorInput.value;
    }
    
    setValue(color) {
        this.colorInput.value = color;
        this.hexInput.value = color.toUpperCase();
        this.circle.style.backgroundColor = color;
    }
}

// Auto-initialize all color pickers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize horizontal color pickers (QR Generator style)
    document.querySelectorAll('.custom-color-picker').forEach(element => {
        new ColorPicker(element);
    });
    
    // Initialize vertical color pickers (CSV Table style)
    document.querySelectorAll('.csv-color-picker').forEach(element => {
        new ColorPicker(element);
    });
});

// Export for manual initialization if needed
window.ColorPicker = ColorPicker;
