/**
 * Main JavaScript file for Speech Emotion Recognition system
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // File upload validation
    const audioFileInput = document.getElementById('audioFile');
    if (audioFileInput) {
        audioFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            // Check if file is selected
            if (!file) {
                return;
            }
            
            // Check file size (max 16MB)
            const maxSize = 16 * 1024 * 1024; // 16MB in bytes
            if (file.size > maxSize) {
                alert('File size exceeds 16MB limit. Please select a smaller file.');
                e.target.value = ''; // Clear the file input
                return;
            }
            
            // Check file type
            const acceptedTypes = ['audio/wav', 'audio/mpeg', 'audio/ogg'];
            if (!acceptedTypes.includes(file.type)) {
                alert('Invalid file type. Please select a WAV, MP3, or OGG file.');
                e.target.value = ''; // Clear the file input
                return;
            }
        });
    }
    
    // Automatically close alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        if (!alert.classList.contains('alert-info')) {
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
    
    // Enable tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Training form validation
    const trainForm = document.querySelector('form[action*="train/start"]');
    if (trainForm) {
        trainForm.addEventListener('submit', function(e) {
            const epochsInput = document.getElementById('epochs');
            if (epochsInput) {
                const epochs = parseInt(epochsInput.value);
                if (isNaN(epochs) || epochs < 1 || epochs > 100) {
                    e.preventDefault();
                    alert('Please enter a valid number of epochs between 1 and 100.');
                    return false;
                }
            }
            
            // Show loading spinner
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
                submitButton.disabled = true;
            }
            
            return true;
        });
    }
});
