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

    // Q&A functionality
    const questionInput = document.getElementById('questionInput');
    const askBtn = document.getElementById('askBtn');
    const responseOutput = document.getElementById('responseOutput');
    
    if (questionInput && askBtn && responseOutput) {
        askBtn.addEventListener('click', askQuestion);
        
        // Allow Enter to ask question (Ctrl+Enter or Cmd+Enter)
        questionInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
                event.preventDefault();
                askQuestion();
            }
        });
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
            // Create audio blob
            const blob = new Blob(recordedChunks, { type: 'audio/webm' });
            
            // Show processing message
            showEchoStatus('🎉 Recording complete! Processing with AI Voice Chatbot...', 'loading');
            
            // Process with AI Voice Chatbot (transcribe + LLM + TTS)
            processEchoBot(blob);
            
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
        
        // Auto-hide success messages after 15 seconds (increased for transcription results)
        if (type === "success") {
            setTimeout(() => {
                if (echoOutput.textContent === message) {
                    echoOutput.textContent = "";
                    echoOutput.className = "status-message";
                }
            }, 15000);
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

// Process audio through AI Voice Chatbot (transcribe + LLM + TTS)
async function processEchoBot(audioBlob) {
    try {
        // Create FormData for AI voice chatbot processing
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'recording.webm');
        
        // Show processing progress
        showEchoStatus('🎤 Transcribing audio with AssemblyAI...', 'loading');
        
        // Send to LLM query endpoint
        const response = await fetch('/llm/query', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            // Show processing stages
            const transcriptionText = result.input_text || "No speech detected";
            const aiResponse = result.response_text || "No AI response generated";
            
            // Update status to show LLM processing
            showEchoStatus('🤖 AI is processing your question...', 'loading');
            
            // Brief delay to show LLM processing
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Update status to show TTS generation
            showEchoStatus('🎵 Generating AI response with Murf voice...', 'loading');
            
            // Set up audio player with Murf-generated AI response
            const echoPlayer = document.getElementById('echoPlayer');
            if (result.audio_file) {
                echoPlayer.src = result.audio_file;
                echoPlayer.style.display = 'block';
            }
            
            // Show final result
            const chatbotDisplay = `✅ AI Voice Chatbot Complete!

🎯 You asked:
"${transcriptionText}"

🤖 AI Response:
"${aiResponse}"

🎵 Click play to hear the AI response!`;
            
            showEchoStatus(chatbotDisplay, 'success');
            
            // Auto-play the AI response audio (if allowed by browser)
            if (result.audio_file) {
                try {
                    await echoPlayer.play();
                    console.log("AI response audio started playing automatically");
                } catch (autoplayError) {
                    console.log("Autoplay prevented by browser - user can click play manually");
                }
            }
            
            console.log('🤖 Full AI Voice Chatbot API Response:', result);
        } else {
            throw new Error(result.detail || result.message || 'AI Voice Chatbot processing failed');
        }
        
    } catch (error) {
        console.error('AI Voice Chatbot error:', error);
        showEchoStatus(
            `❌ AI Voice Chatbot failed: ${error.message}. Please try again.`, 
            'error'
        );
    }
}

console.log("🚀 VoiceForge platform ready!");