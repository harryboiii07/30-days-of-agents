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

console.log("🚀 VoiceForge platform ready!");