/**
 * Enhanced JavaScript for Speech Emotion Recognition system
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // File upload validation and styling
    const audioFileInput = document.getElementById('audioFile');
    if (audioFileInput) {
        const fileUploadContainer = document.querySelector('.file-upload-container');
        
        audioFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            // Check if file is selected
            if (!file) {
                return;
            }
            
            // Check file size (max 16MB)
            const maxSize = 16 * 1024 * 1024; // 16MB in bytes
            if (file.size > maxSize) {
                showToast('File size exceeds 16MB limit. Please select a smaller file.', 'danger');
                e.target.value = ''; // Clear the file input
                return;
            }
            
            // Check file type
            const acceptedTypes = ['audio/wav', 'audio/mpeg', 'audio/ogg'];
            if (!acceptedTypes.includes(file.type)) {
                showToast('Invalid file type. Please select a WAV, MP3, or OGG file.', 'danger');
                e.target.value = ''; // Clear the file input
                return;
            }
            
            // Update file selection UI
            if (fileUploadContainer) {
                const fileName = file.name;
                fileUploadContainer.querySelector('p').textContent = `Selected: ${fileName}`;
                const iconElement = fileUploadContainer.querySelector('i');
                if (iconElement) {
                    iconElement.classList.remove('fa-file-audio');
                    iconElement.classList.add('fa-check-circle');
                }
                fileUploadContainer.classList.add('border-success');
            }
        });
    }
    
    // Create a toast notification function
    function showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create the toast
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.className = `toast show align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.id = toastId;
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'danger' ? 'exclamation-circle' : 
                                     type === 'success' ? 'check-circle' : 
                                     type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Add the toast to the container
        toastContainer.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (document.getElementById(toastId)) {
                toast.classList.remove('show');
                setTimeout(() => {
                    if (document.getElementById(toastId)) {
                        toastContainer.removeChild(toast);
                    }
                }, 300);
            }
        }, 5000);
        
        // Make close button work
        const closeButton = toast.querySelector('.btn-close');
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                toast.classList.remove('show');
                setTimeout(() => {
                    if (document.getElementById(toastId)) {
                        toastContainer.removeChild(toast);
                    }
                }, 300);
            });
        }
    }
    
    // Enhanced animations for page elements
    const animateElements = () => {
        // Define animation style if not already added
        if (!document.getElementById('animation-styles')) {
            const styleElement = document.createElement('style');
            styleElement.id = 'animation-styles';
            styleElement.textContent = `
                @keyframes fadeInUp {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes slideInRight {
                    from { opacity: 0; transform: translateX(20px); }
                    to { opacity: 1; transform: translateX(0); }
                }
                .animate-fadeInUp {
                    animation: fadeInUp 0.5s ease forwards;
                }
                .animate-fadeIn {
                    animation: fadeIn 0.5s ease forwards;
                }
                .animate-slideInRight {
                    animation: slideInRight 0.5s ease forwards;
                }
                .delayed-animation {
                    opacity: 0;
                }
            `;
            document.head.appendChild(styleElement);
        }
        
        // Apply animations to card elements with delay
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('animate-fadeInUp');
            }, index * 100);
        });
        
        // Apply animations to emotion grid items
        const emotionItems = document.querySelectorAll('.emotion-item');
        emotionItems.forEach((item, index) => {
            item.style.opacity = '0';
            setTimeout(() => {
                item.style.animation = 'fadeInUp 0.5s ease forwards';
                item.style.opacity = '1';
            }, 300 + (index * 50));
        });
    };
    
    // Run animations after page load
    setTimeout(animateElements, 100);
    
    // Recording functionality
    const setupRecording = () => {
        // Check if we're on the record tab
        const recordTab = document.getElementById('record-tab');
        if (!recordTab) return;
        
        // Elements
        const startRecordButton = document.getElementById('startRecording');
        const stopRecordButton = document.getElementById('stopRecording');
        const analyzeButton = document.getElementById('analyzeRecording');
        const discardButton = document.getElementById('discardRecording');
        const retryButton = document.getElementById('retryRecording');
        const recordingStatus = document.getElementById('recordingStatus');
        const recordingControls = document.getElementById('recordingControls');
        const recordingResult = document.getElementById('recordingResult');
        const recordingError = document.getElementById('recordingError');
        const recordedAudio = document.getElementById('recordedAudio');
        const recordingTime = document.getElementById('recordingTime');
        const errorMessage = document.getElementById('errorMessage');
        const recordingProgress = document.getElementById('recordingProgress');
        
        // Variables
        let mediaRecorder;
        let audioChunks = [];
        let startTime;
        let timerInterval;
        let audioBlob;
        const MAX_RECORDING_TIME = 30; // seconds
        
        // Event listeners
        if (startRecordButton) {
            startRecordButton.addEventListener('click', startRecording);
        }
        
        if (stopRecordButton) {
            stopRecordButton.addEventListener('click', stopRecording);
        }
        
        if (analyzeButton) {
            analyzeButton.addEventListener('click', analyzeRecording);
        }
        
        if (discardButton) {
            discardButton.addEventListener('click', discardRecording);
        }
        
        if (retryButton) {
            retryButton.addEventListener('click', retryRecording);
        }
        
        // Functions
        function startRecording() {
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    audioChunks = [];
                    mediaRecorder = new MediaRecorder(stream);
                    
                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = () => {
                        const tracks = mediaRecorder.stream.getTracks();
                        tracks.forEach(track => track.stop());
                        
                        audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const audioUrl = URL.createObjectURL(audioBlob);
                        recordedAudio.src = audioUrl;
                        
                        stopTimer();
                        showRecordingResult();
                    };
                    
                    mediaRecorder.start();
                    startTimer();
                    showRecordingStatus();
                    
                    // Pulse animation for recording indicator
                    const recordingIndicator = document.getElementById('recordingIndicator');
                    if (recordingIndicator) {
                        recordingIndicator.animate([
                            { opacity: 1, transform: 'scale(1)' },
                            { opacity: 0.5, transform: 'scale(0.9)' },
                            { opacity: 1, transform: 'scale(1)' }
                        ], {
                            duration: 1000,
                            iterations: Infinity
                        });
                    }
                    
                    // Stop after MAX_RECORDING_TIME seconds automatically
                    setTimeout(() => {
                        if (mediaRecorder && mediaRecorder.state === 'recording') {
                            stopRecording();
                        }
                    }, MAX_RECORDING_TIME * 1000);
                })
                .catch(error => {
                    console.error('Error accessing microphone:', error);
                    errorMessage.textContent = 'Error accessing microphone: ' + error.message;
                    showRecordingError();
                });
        }
        
        function stopRecording() {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
                showToast('Recording completed!', 'success');
            }
        }
        
        function analyzeRecording() {
            if (!audioBlob) return;
            
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');
            
            // Show loading spinner
            analyzeButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Analyzing...';
            analyzeButton.disabled = true;
            discardButton.disabled = true;
            
            // Add progress animation
            const progressAlert = document.createElement('div');
            progressAlert.className = 'alert alert-info mt-3';
            progressAlert.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
                    <div>
                        <p class="mb-0">Processing your recording. This may take a moment...</p>
                    </div>
                </div>
            `;
            recordingResult.appendChild(progressAlert);
            
            // Send to server
            fetch('/process-recording', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Smooth transition to results page
                showToast('Analysis complete! Redirecting to results...', 'success');
                
                // Add transition effect
                document.body.style.transition = 'opacity 0.3s ease';
                document.body.style.opacity = '0.5';
                setTimeout(() => {
                    window.location.href = '/results/' + data.id;
                }, 800);
            })
            .catch(error => {
                console.error('Error:', error);
                analyzeButton.innerHTML = '<i class="fas fa-play-circle me-2"></i>Analyze Emotion';
                analyzeButton.disabled = false;
                discardButton.disabled = false;
                
                // Remove progress alert
                if (progressAlert && progressAlert.parentNode) {
                    progressAlert.parentNode.removeChild(progressAlert);
                }
                
                errorMessage.textContent = 'Error processing recording: ' + error.message;
                showRecordingError();
                showToast('Error processing recording. Please try again.', 'danger');
            });
        }
        
        function discardRecording() {
            audioBlob = null;
            recordedAudio.src = '';
            showRecordingControls();
            showToast('Recording discarded', 'info');
        }
        
        function retryRecording() {
            showRecordingControls();
        }
        
        function startTimer() {
            startTime = Date.now();
            updateTimer();
            timerInterval = setInterval(updateTimer, 1000);
        }
        
        function stopTimer() {
            clearInterval(timerInterval);
        }
        
        function updateTimer() {
            const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
            const minutes = Math.floor(elapsedTime / 60).toString().padStart(2, '0');
            const seconds = (elapsedTime % 60).toString().padStart(2, '0');
            recordingTime.textContent = `${minutes}:${seconds}`;
            
            // Update progress bar
            if (recordingProgress) {
                const progressPercentage = (elapsedTime / MAX_RECORDING_TIME) * 100;
                recordingProgress.style.width = Math.min(progressPercentage, 100) + '%';
                recordingProgress.setAttribute('aria-valuenow', Math.min(progressPercentage, 100));
                
                // Change color as it gets closer to max time
                if (progressPercentage > 80) {
                    recordingProgress.classList.add('bg-danger');
                    recordingProgress.classList.remove('bg-warning');
                } else if (progressPercentage > 60) {
                    recordingProgress.classList.add('bg-warning');
                    recordingProgress.classList.remove('bg-danger');
                }
            }
        }
        
        function showRecordingStatus() {
            recordingStatus.classList.remove('d-none');
            recordingControls.classList.add('d-none');
            recordingResult.classList.add('d-none');
            recordingError.classList.add('d-none');
            startRecordButton.classList.add('d-none');
            stopRecordButton.classList.remove('d-none');
        }
        
        function showRecordingResult() {
            recordingStatus.classList.add('d-none');
            recordingControls.classList.add('d-none');
            recordingResult.classList.remove('d-none');
            recordingError.classList.add('d-none');
            startRecordButton.classList.remove('d-none');
            stopRecordButton.classList.add('d-none');
            
            // Animate the result container appearance
            recordingResult.style.animation = 'fadeIn 0.5s forwards';
        }
        
        function showRecordingControls() {
            recordingStatus.classList.add('d-none');
            recordingControls.classList.remove('d-none');
            recordingResult.classList.add('d-none');
            recordingError.classList.add('d-none');
            startRecordButton.classList.remove('d-none');
            stopRecordButton.classList.add('d-none');
        }
        
        function showRecordingError() {
            recordingStatus.classList.add('d-none');
            recordingControls.classList.add('d-none');
            recordingResult.classList.add('d-none');
            recordingError.classList.remove('d-none');
            
            // Animate the error container appearance
            recordingError.style.animation = 'fadeIn 0.5s forwards';
        }
    };
    
    // Setup the recording functionality
    setupRecording();
    
    // Tab switching animation
    const setupTabAnimations = () => {
        const inputTabs = document.querySelectorAll('#inputTabs button');
        if (inputTabs.length > 0) {
            inputTabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    const tabPanes = document.querySelectorAll('.tab-pane');
                    tabPanes.forEach(pane => {
                        pane.style.animation = 'none';
                    });
                    
                    setTimeout(() => {
                        const tabContent = document.querySelector(this.dataset.bsTarget);
                        if (tabContent) {
                            tabContent.style.animation = 'fadeIn 0.4s forwards';
                        }
                    }, 50);
                });
            });
        }
    };
    
    // Setup tab animations
    setupTabAnimations();
    
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
    
    // Training form validation with enhanced UX
    const trainForm = document.querySelector('form[action*="train/start"]');
    if (trainForm) {
        trainForm.addEventListener('submit', function(e) {
            const epochsInput = document.getElementById('epochs');
            if (epochsInput) {
                const epochs = parseInt(epochsInput.value);
                if (isNaN(epochs) || epochs < 1 || epochs > 100) {
                    e.preventDefault();
                    showToast('Please enter a valid number of epochs between 1 and 100.', 'warning');
                    epochsInput.focus();
                    epochsInput.classList.add('is-invalid');
                    
                    // Add validation feedback
                    let feedback = epochsInput.nextElementSibling;
                    if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                        feedback = document.createElement('div');
                        feedback.className = 'invalid-feedback';
                        epochsInput.parentNode.appendChild(feedback);
                    }
                    feedback.textContent = 'Please enter a number between 1 and 100.';
                    
                    return false;
                } else {
                    epochsInput.classList.remove('is-invalid');
                    epochsInput.classList.add('is-valid');
                }
            }
            
            // Show loading spinner with text
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Starting training process...';
                submitButton.disabled = true;
                
                // Add a progress message
                const progressMsg = document.createElement('div');
                progressMsg.className = 'alert alert-info mt-3';
                progressMsg.innerHTML = `
                    <div class="d-flex align-items-center">
                        <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
                        <div>
                            <h5 class="mb-1">Training in progress</h5>
                            <p class="mb-0">This may take several minutes. Please don't close this page.</p>
                        </div>
                    </div>
                `;
                
                trainForm.parentNode.appendChild(progressMsg);
            }
            
            return true;
        });
        
        // Real-time validation as user types
        const epochsInput = document.getElementById('epochs');
        if (epochsInput) {
            epochsInput.addEventListener('input', function() {
                const epochs = parseInt(this.value);
                if (isNaN(epochs) || epochs < 1 || epochs > 100) {
                    this.classList.add('is-invalid');
                    this.classList.remove('is-valid');
                } else {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
        }
    }
});
