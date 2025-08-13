// VoiceForge - Professional Text-to-Speech Platform JavaScript
console.log("🎤 VoiceForge - Text-to-Speech Platform loaded!");

// Session management
let currentSessionId = null;
let autoRecordEnabled = false;

// Initialize or get session ID from URL params
function initializeSession() {
    const urlParams = new URLSearchParams(window.location.search);
    currentSessionId = urlParams.get('session_id');
    
    if (!currentSessionId) {
        // Generate new session ID
        currentSessionId = generateSessionId();
        // Update URL with session ID
        const newUrl = new URL(window.location);
        newUrl.searchParams.set('session_id', currentSessionId);
        window.history.pushState(null, '', newUrl.toString());
    }
    
    console.log("🆔 Session ID:", currentSessionId);
    updateSessionDisplay();
}

function generateSessionId() {
    return 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function updateSessionDisplay() {
    const sessionDisplay = document.getElementById('sessionDisplay');
    if (sessionDisplay) {
        sessionDisplay.textContent = `Session: ${currentSessionId}`;
    }
}

// DOM Content Loaded Event
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");
    initializeSession();
    initializePage();
});

function initializePage() {
    // Voice Chatbot functionality
    const micBtn = document.getElementById('micBtn');
    const clearChatBtn = document.getElementById('clearChatBtn');
    
    if (micBtn) {
        micBtn.addEventListener('click', handleMicClick);
        
        // Check browser support
        if (!checkVoiceChatSupport()) {
            micBtn.disabled = true;
            updateMicStatus('Browser not supported');
        }
    }
    
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', clearChat);
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
    
    // Auto-scroll to voice chatbot section
    setTimeout(() => {
        const voiceChatSection = document.getElementById('voice-chatbot');
        if (voiceChatSection) {
            const navHeight = document.querySelector('.navbar').offsetHeight;
            const targetPosition = voiceChatSection.offsetTop - navHeight - 20;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    }, 500);
}





// Voice Chat Variables
let mediaRecorder = null;
let recordedChunks = [];
let isRecording = false;
let isProcessing = false;
let recordingTimer = null;
let recordingStartTime = 0;
let currentAudio = null;

// New Voice Chat Functions
function handleMicClick() {
    if (isProcessing) {
        return; // Don't allow clicks while processing
    }
    
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

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
            
            // Start processing
            processVoiceMessage(blob);
            
            // Stop all tracks to free up microphone
            stream.getTracks().forEach(track => track.stop());
        };
        
        // Start recording
        mediaRecorder.start();
        isRecording = true;
        recordingStartTime = Date.now();
        
        // Update UI
        updateMicButton('recording');
        updateMicStatus('Recording...');
        startRecordingTimer();
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        updateMicStatus('Microphone access denied');
        addSystemMessage('❌ Could not access microphone. Please check permissions.');
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        // Update UI
        updateMicButton('processing');
        updateMicStatus('Processing...');
        stopRecordingTimer();
    }
}

// UI Helper Functions
function updateMicButton(state) {
    const micBtn = document.getElementById('micBtn');
    if (micBtn) {
        micBtn.setAttribute('data-state', state);
        micBtn.disabled = (state === 'processing');
    }
}

function updateMicStatus(status) {
    const micStatus = document.getElementById('micStatus');
    if (micStatus) {
        micStatus.textContent = status;
    }
}

function updateProgress(step, percentage) {
    const progressContainer = document.getElementById('progressContainer');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    if (progressContainer && progressFill && progressText) {
        progressContainer.style.display = percentage > 0 ? 'block' : 'none';
        progressFill.style.width = percentage + '%';
        progressText.textContent = step;
    }
}

function hideProgress() {
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.style.display = 'none';
    }
}

// Message Functions
function addUserMessage(text) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="user-avatar">👤</div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
            <div class="message-timestamp">${getCurrentTime()}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function addAiMessage(text, audioUrl = null) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai';
    
    let audioHtml = '';
    if (audioUrl) {
        audioHtml = `<div class="message-audio">
            <audio controls preload="none" onended="handleAudioEnd()">
                <source src="${audioUrl}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
        </div>`;
    }
    
    messageDiv.innerHTML = `
        <div class="ai-avatar">🤖</div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
            ${audioHtml}
            <div class="message-timestamp">${getCurrentTime()}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    
    // Auto-play the audio if provided
    if (audioUrl) {
        const audio = messageDiv.querySelector('audio');
        if (audio) {
            currentAudio = audio;
            try {
                audio.play();
            } catch (e) {
                console.log('Autoplay prevented - user can click play manually');
            }
        }
    }
}

function addSystemMessage(text) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'welcome-message';
    messageDiv.innerHTML = `
        <div class="ai-avatar">ℹ️</div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Utility Functions
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getCurrentTime() {
    return new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function startRecordingTimer() {
    recordingTimer = setInterval(() => {
        updateRecordingTimer();
    }, 100);
}

function stopRecordingTimer() {
    if (recordingTimer) {
        clearInterval(recordingTimer);
        recordingTimer = null;
    }
    
    // Reset timer display
    setTimeout(() => {
        const recordingTimer = document.getElementById('recordingTimer');
        if (recordingTimer) {
            recordingTimer.textContent = '00:00';
        }
    }, 2000);
}



// Process voice message with progress tracking and error handling
async function processVoiceMessage(audioBlob) {
    try {
        isProcessing = true;
        updateMicButton('processing');
        
        // Step 1: Transcribing
        updateProgress('🎤 Transcribing your voice...', 25);
        
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'recording.webm');
        
        let response, result;
        
        try {
            response = await fetch(`/agent/chat/${currentSessionId}`, {
                method: 'POST',
                body: formData
            });
            result = await response.json();
        } catch (networkError) {
            console.error('Network error:', networkError);
            throw new Error('Unable to connect to the server. Please check your internet connection.');
        }
        
        // Handle API errors with user-friendly messages
        if (!response.ok || !result.success) {
            const errorMessage = result.message || result.detail || 'Processing failed';
            
            // Play fallback audio if available or use text-to-speech fallback
            if (result.fallback_audio) {
                await playFallbackAudio(result.fallback_audio);
            } else {
                await playFallbackMessage(errorMessage);
            }
            
            throw new Error(errorMessage);
        }
        
        const userMessage = result.user_message || "No speech detected";
        const aiResponse = result.ai_response || "No AI response generated";
        
        // Step 2: Show user message
        updateProgress('✅ Transcription complete', 50);
        addUserMessage(userMessage);
        
        // Step 3: AI Processing
        updateProgress('🤖 AI is thinking...', 75);
        await new Promise(resolve => setTimeout(resolve, 1000)); // Brief pause for UX
        
        // Step 4: Complete
        updateProgress('🎵 Generating voice response...', 90);
        await new Promise(resolve => setTimeout(resolve, 500));
        
        updateProgress('✅ Complete!', 100);
        
        // Add AI message with audio (or fallback if audio failed)
        if (result.audio_file) {
            addAiMessage(aiResponse, result.audio_file);
        } else {
            // If TTS failed, still show the text response
            addAiMessage(aiResponse);
            console.warn('Audio generation failed, showing text-only response');
        }
        
        // Hide progress after a delay
        setTimeout(() => {
            hideProgress();
            updateMicButton('ready');
            updateMicStatus('Tap to start');
            isProcessing = false;
        }, 1000);
        
        console.log('🤖 Voice chat processed successfully:', result);
        
    } catch (error) {
        console.error('Voice processing error:', error);
        hideProgress();
        
        // Show user-friendly error message
        let errorMessage = error.message;
        if (errorMessage.includes('fetch')) {
            errorMessage = "I'm having trouble connecting right now. Please check your internet connection and try again.";
        } else if (errorMessage.includes('timeout')) {
            errorMessage = "The request is taking too long. Please try again.";
        }
        
        addSystemMessage(`❌ ${errorMessage}`);
        
        // Try to play audio fallback for common errors
        if (error.message.includes('connect') || error.message.includes('network')) {
            await playFallbackMessage("I'm having trouble connecting right now. Please try again.");
        }
        
        updateMicButton('ready');
        updateMicStatus('Tap to start');
        isProcessing = false;
    }
}

// Handle audio playback end for auto-recording
function handleAudioEnd() {
    if (!isProcessing && !isRecording) {
        console.log("🔄 Audio ended, auto-enabling microphone...");
        setTimeout(() => {
            if (!isProcessing && !isRecording) {
                updateMicButton('ready');
                updateMicStatus('Ready - tap to speak');
                // Flash the mic button to indicate it's ready
                const micBtn = document.getElementById('micBtn');
                if (micBtn) {
                    micBtn.style.animation = 'pulse 1s ease-in-out 2';
                    setTimeout(() => {
                        micBtn.style.animation = '';
                    }, 2000);
                }
            }
        }, 1000);
    }
}

// Clear chat and start new session
function clearChat() {
    // Generate new session ID
    currentSessionId = generateSessionId();
    
    // Update URL
    const newUrl = new URL(window.location);
    newUrl.searchParams.set('session_id', currentSessionId);
    window.history.pushState(null, '', newUrl.toString());
    
    // Update UI
    updateSessionDisplay();
    
    // Clear chat messages
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="ai-avatar">🤖</div>
                <div class="message-content">
                    <div class="message-text">Hi! I'm your AI voice assistant. Press the microphone button to start our conversation!</div>
                </div>
            </div>
        `;
    }
    
    // Reset state
    isRecording = false;
    isProcessing = false;
    hideProgress();
    updateMicButton('ready');
    updateMicStatus('Tap to start');
    
    console.log('🔄 Chat cleared, new session started:', currentSessionId);
}

// Update recording timer display
function updateRecordingTimer() {
    const recordingTimer = document.getElementById('recordingTimer');
    if (recordingTimer && isRecording) {
        const elapsed = Date.now() - recordingStartTime;
        const seconds = Math.floor(elapsed / 1000);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        
        const timeString = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
        recordingTimer.textContent = timeString;
    }
}

// Check browser support for voice chat
function checkVoiceChatSupport() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.error('MediaDevices not supported');
        return false;
    }
    
    if (!window.MediaRecorder) {
        console.error('MediaRecorder not supported');
        return false;
    }
    
    return true;
}

// Fallback audio functions
async function playFallbackMessage(message) {
    try {
        // Use browser's built-in speech synthesis as fallback
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(message);
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            utterance.volume = 0.8;
            
            // Try to use a natural-sounding voice
            const voices = speechSynthesis.getVoices();
            const preferredVoice = voices.find(voice => 
                voice.lang.startsWith('en') && 
                (voice.name.includes('Google') || voice.name.includes('Microsoft') || voice.name.includes('Samantha'))
            );
            
            if (preferredVoice) {
                utterance.voice = preferredVoice;
            }
            
            speechSynthesis.speak(utterance);
            console.log('🔊 Playing fallback message using browser TTS');
        } else {
            console.warn('Speech synthesis not available in this browser');
        }
    } catch (error) {
        console.error('Fallback audio error:', error);
    }
}

async function playFallbackAudio(audioUrl) {
    try {
        const audio = new Audio(audioUrl);
        await audio.play();
        console.log('🔊 Playing fallback audio from server');
    } catch (error) {
        console.error('Fallback audio playback error:', error);
        // If fallback audio fails, use speech synthesis
        await playFallbackMessage("I'm having trouble right now. Please try again.");
    }
}

// Enhanced error handling for TTS generation
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
        
        let response, data;
        
        try {
            // Make API request with timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
            
            response = await fetch('/api/tts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    voice_id: voiceSelect.value
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            data = await response.json();
            
        } catch (networkError) {
            if (networkError.name === 'AbortError') {
                throw new Error('Request timed out. Please try again with shorter text.');
            }
            throw new Error('Unable to connect to the text-to-speech service.');
        }
        
        if (data.success && data.audio_file) {
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
            const errorMessage = data.message || "Unknown error occurred while generating speech";
            showStatusMessage(`❌ ${errorMessage}`, "error");
            
            // Provide fallback using browser TTS
            if (text.length < 500) { // Only for shorter texts
                console.log('Attempting fallback using browser speech synthesis');
                await playFallbackMessage(text);
                showStatusMessage(`⚠️ Using browser fallback audio. For better quality, please try again later.`, "error");
            }
        }
        
    } catch (error) {
        console.error('TTS Error:', error);
        let errorMessage = error.message;
        
        if (errorMessage.includes('connect') || errorMessage.includes('network')) {
            errorMessage = "Unable to connect to the speech service. Please check your internet connection.";
        } else if (errorMessage.includes('timeout')) {
            errorMessage = "The request timed out. Please try again with shorter text.";
        }
        
        showStatusMessage(`❌ ${errorMessage}`, "error");
        
        // Try browser fallback for short texts
        const text = textInput.value.trim();
        if (text && text.length < 500) {
            try {
                await playFallbackMessage(text);
                showStatusMessage(`⚠️ Using browser fallback audio. For better quality, please try again later.`, "error");
            } catch (fallbackError) {
                console.error('Fallback TTS also failed:', fallbackError);
            }
        }
    } finally {
        // Reset button state
        generateBtn.disabled = false;
    }
}

console.log("🚀 VoiceForge platform ready with enhanced error handling!");