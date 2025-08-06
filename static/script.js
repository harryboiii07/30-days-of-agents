// VoiceForge - Professional Text-to-Speech Platform JavaScript
console.log("🎤 VoiceForge - Text-to-Speech Platform loaded!");

// DOM Content Loaded Event
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");
    initializePage();
});

function initializePage() {
    // Text-to-Speech functionality
    const generateBtn = document.getElementById('generateBtn');
    const textInput = document.getElementById('textInput');
    const voiceSelect = document.getElementById('voiceSelect');
    const ttsOutput = document.getElementById('ttsOutput');
    const audioPlayer = document.getElementById('audioPlayer');
    
    if (generateBtn && textInput && voiceSelect && ttsOutput && audioPlayer) {
        generateBtn.addEventListener('click', generateSpeech);
        
        // Allow Enter key to submit (when not in textarea)
        textInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && event.ctrlKey) {
                event.preventDefault();
                generateSpeech();
            }
        });
    }

    // Echo Bot functionality
    const startRecordBtn = document.getElementById('startRecordBtn');
    const stopRecordBtn = document.getElementById('stopRecordBtn');
    
    if (startRecordBtn && stopRecordBtn) {
        startRecordBtn.addEventListener('click', startRecording);
        stopRecordBtn.addEventListener('click', stopRecording);
        
        // Set initial button states
        updateRecordingUI();
        
        // Check browser support
        if (!checkEchoBotSupport()) {
            startRecordBtn.disabled = true;
            stopRecordBtn.disabled = true;
        }
    }

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const navHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = target.offsetTop - navHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(255, 255, 255, 0.98)';
            navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.boxShadow = 'none';
        }
    });
}

async function generateSpeech() {
    const generateBtn = document.getElementById('generateBtn');
    const textInput = document.getElementById('textInput');
    const voiceSelect = document.getElementById('voiceSelect');
    const ttsOutput = document.getElementById('ttsOutput');
    const audioPlayer = document.getElementById('audioPlayer');
    
    try {
        const text = textInput.value.trim();
        
        if (!text) {
            showStatusMessage("Please enter some text to convert to speech.", "error");
            return;
        }

        if (text.length > 5000) {
            showStatusMessage("Text is too long. Please limit to 5000 characters.", "error");
            return;
        }
        
        // Show loading state
        generateBtn.disabled = true;
        showStatusMessage("🎵 Generating high-quality audio... This may take a few seconds.", "loading");
        audioPlayer.style.display = "none";
        audioPlayer.removeAttribute('src');
        
        // Make API request
        const response = await fetch('/api/tts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                voice_id: voiceSelect.value
            })
        });
        
                const data = await response.json();
                
        if (response.ok && data.success) {
            showStatusMessage(`✅ Audio generated successfully! Click play to listen.`, "success");
            
            // Set up audio player
            audioPlayer.src = data.audio_file;
            audioPlayer.style.display = "block";
            
            // Scroll audio into view
            audioPlayer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            
            // Auto-play the audio (if allowed by browser)
            try {
                await audioPlayer.play();
                console.log("Audio started playing automatically");
            } catch (autoplayError) {
                console.log("Autoplay prevented by browser - user can click play manually");
            }
                } else {
            const errorMessage = data.detail || data.message || "Unknown error occurred";
            showStatusMessage(`❌ Error: ${errorMessage}`, "error");
        }
        
    } catch (error) {
        console.error('TTS Error:', error);
        showStatusMessage(`❌ Network Error: ${error.message}`, "error");
    } finally {
        // Reset button state
        generateBtn.disabled = false;
    }
}

function showStatusMessage(message, type = "loading") {
    const ttsOutput = document.getElementById('ttsOutput');
    if (ttsOutput) {
        ttsOutput.textContent = message;
        ttsOutput.className = `status-message ${type}`;
        
        // Auto-hide success messages after 5 seconds
        if (type === "success") {
            setTimeout(() => {
                if (ttsOutput.textContent === message) {
                    ttsOutput.textContent = "";
                    ttsOutput.className = "status-message";
                }
            }, 5000);
        }
    }
}

// Echo Bot Variables
let mediaRecorder = null;
let recordedChunks = [];
let recording = false;
let recordingTimer = null;
let recordingStartTime = 0;

async function startRecording() {
    try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            } 
        });
        
        // Initialize MediaRecorder
        recordedChunks = [];
        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm;codecs=opus'
        });
        
        // Set up event handlers
        mediaRecorder.ondataavailable = function(event) {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = function() {
            // Create audio blob and URL
            const blob = new Blob(recordedChunks, { type: 'audio/webm' });
            const audioUrl = URL.createObjectURL(blob);
            
            // Set up audio player
            const echoPlayer = document.getElementById('echoPlayer');
            echoPlayer.src = audioUrl;
            echoPlayer.style.display = 'block';
            
            // Show processing message
            showEchoStatus('🎉 Recording complete! Uploading to server...', 'loading');
            
            // Upload audio file to server
            uploadAudioFile(blob);
            
            // Stop all tracks to free up microphone
            stream.getTracks().forEach(track => track.stop());
        };
        
        // Start recording
        mediaRecorder.start();
        recording = true;
        recordingStartTime = Date.now();
        
        // Update UI
        updateRecordingUI();
        showEchoStatus('🎤 Recording... Speak into your microphone!', 'loading');
        
        // Start timer
        startRecordingTimer();
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        showEchoStatus('❌ Error: Could not access microphone. Please check permissions.', 'error');
    }
}

function stopRecording() {
    if (mediaRecorder && recording) {
        mediaRecorder.stop();
        recording = false;
        
        // Update UI
        updateRecordingUI();
        showEchoStatus('⏳ Processing recording...', 'loading');
        
        // Stop timer
        stopRecordingTimer();
    }
}

function updateRecordingUI() {
    const startBtn = document.getElementById('startRecordBtn');
    const stopBtn = document.getElementById('stopRecordBtn');
    const indicator = document.getElementById('recordingIndicator');
    const status = document.getElementById('recordingStatus');
    
    if (recording) {
        // During recording: disable start, enable stop
        startBtn.disabled = true;
        stopBtn.disabled = false;
        indicator.classList.add('recording');
        status.textContent = 'Recording...';
    } else {
        // Not recording: enable start, disable stop
        startBtn.disabled = false;
        stopBtn.disabled = true;
        indicator.classList.remove('recording');
        status.textContent = 'Ready to Record';
    }
}

function startRecordingTimer() {
    const timeDisplay = document.getElementById('recordingTime');
    
    recordingTimer = setInterval(() => {
        const elapsed = Date.now() - recordingStartTime;
        const seconds = Math.floor(elapsed / 1000);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        
        const timeString = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
        timeDisplay.textContent = timeString;
    }, 100);
}

function stopRecordingTimer() {
    if (recordingTimer) {
        clearInterval(recordingTimer);
        recordingTimer = null;
    }
    
    // Reset timer display
    setTimeout(() => {
        document.getElementById('recordingTime').textContent = '00:00';
    }, 2000);
}

function showEchoStatus(message, type = "loading") {
    const echoOutput = document.getElementById('echoOutput');
    if (echoOutput) {
        echoOutput.textContent = message;
        echoOutput.className = `status-message ${type}`;
        
        // Auto-hide success messages after 5 seconds
        if (type === "success") {
            setTimeout(() => {
                if (echoOutput.textContent === message) {
                    echoOutput.textContent = "";
                    echoOutput.className = "status-message";
                }
            }, 5000);
        }
    }
}

// Check for MediaRecorder support
function checkEchoBotSupport() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showEchoStatus('❌ Your browser does not support audio recording.', 'error');
        return false;
    }
    
    if (!window.MediaRecorder) {
        showEchoStatus('❌ Your browser does not support MediaRecorder API.', 'error');
        return false;
    }
    
    return true;
}

// Upload audio file to server
async function uploadAudioFile(audioBlob) {
    try {
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'recording.webm');
        
        // Show upload progress
        showEchoStatus('📤 Uploading audio file to server...', 'loading');
        
        // Upload to server
        const response = await fetch('/api/upload-audio', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            // Show success message with file details
            const fileSize = result.size_mb > 1 
                ? `${result.size_mb} MB` 
                : `${Math.round(result.size_bytes / 1024)} KB`;
            
            // Create JSON response display
            const responseJson = `✅ Upload successful! File: ${result.filename} (${fileSize})

📊 Server Response (JSON):
${JSON.stringify(result, null, 2)}

Click play to hear your echo.`;
            
            showEchoStatus(responseJson, 'success');
            
            console.log('📊 Full Upload API Response:', result);
        } else {
            throw new Error(result.detail || result.message || 'Upload failed');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        showEchoStatus(
            `❌ Upload failed: ${error.message}. Audio is still playable locally.`, 
            'error'
        );
    }
}

console.log("🚀 VoiceForge platform ready!");