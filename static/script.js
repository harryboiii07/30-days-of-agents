// 30 Days of Voice Agents - Day 1 JavaScript
console.log("🎙️ 30 Days of Voice Agents - Day 1 JavaScript loaded!");

// DOM Content Loaded Event
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");
    
    // Initialize the page
    initializePage();
});

function initializePage() {
    // Test button functionality
    const testBtn = document.getElementById('testBtn');
    const output = document.getElementById('output');
    
    if (testBtn && output) {
        testBtn.addEventListener('click', function() {
            output.textContent = "🎉 JavaScript is working perfectly! Welcome to Day 1 of your voice agents journey!";
            output.style.color = "#4CAF50";
            
            // Add some animation
            output.style.opacity = "0";
            setTimeout(() => {
                output.style.opacity = "1";
                output.style.transition = "opacity 0.5s ease-in";
            }, 100);
        });
    }
    
    // API health check functionality
    const healthBtn = document.getElementById('healthBtn');
    const apiOutput = document.getElementById('apiOutput');
    
    if (healthBtn && apiOutput) {
        healthBtn.addEventListener('click', async function() {
            try {
                apiOutput.textContent = "Checking API health...";
                apiOutput.style.color = "#2196F3";
                
                const response = await fetch('/api/health');
                const data = await response.json();
                
                if (response.ok) {
                    apiOutput.textContent = `✅ ${data.message} - Status: ${data.status}`;
                    apiOutput.style.color = "#4CAF50";
                } else {
                    apiOutput.textContent = "❌ API health check failed";
                    apiOutput.style.color = "#f44336";
                }
            } catch (error) {
                apiOutput.textContent = `❌ Error: ${error.message}`;
                apiOutput.style.color = "#f44336";
            }
        });
    }
}

// Utility function for future days
function logDayProgress(day, task) {
    console.log(`📅 Day ${day}: ${task}`);
}

// Log Day 1 completion
logDayProgress(1, "Project Setup - Complete!");

// Export functions for potential future use
window.VoiceAgentsApp = {
    initializePage,
    logDayProgress
};