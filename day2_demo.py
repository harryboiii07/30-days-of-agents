#!/usr/bin/env python3
"""
Day 2 Demonstration Script - TTS Endpoint
Show how to test the /api/tts endpoint for the 30 Days of Voice Agents challenge
"""

import requests
import json

def demo_tts_endpoint():
    """Demonstrate the TTS endpoint for Day 2"""
    
    print("🎙️ 30 Days of Voice Agents - Day 2 Demo")
    print("=" * 50)
    print("Task: Create a TTS endpoint that accepts text and returns audio URL")
    print()
    
    # Test data for demo
    test_cases = [
        {
            "text": "Hello! This is Day 2 of 30 Days of Voice Agents by Murf AI!",
            "voice_id": "en-US-natalie"
        },
        {
            "text": "Welcome to our FastAPI TTS service. This endpoint accepts text and returns an audio URL.",
            "voice_id": "en-US-sarah"
        }
    ]
    
    print("🚀 Testing TTS Endpoint: POST /api/tts")
    print("📍 Server: http://localhost:8000")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 Test {i}:")
        print(f"   Text: {test_case['text']}")
        print(f"   Voice: {test_case['voice_id']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/tts",
                json=test_case,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result.get('success')}")
                print(f"   🎵 Audio URL: {result.get('audio_url')}")
                print(f"   💬 Message: {result.get('message')}")
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   🔥 Connection Error: {e}")
            print("   💡 Make sure the server is running: python main.py")
            
        print()
    
    print("🎯 Day 2 Task Completion:")
    print("✅ Created TTS endpoint that accepts text")
    print("✅ Endpoint returns audio URL structure") 
    print("✅ Proper error handling and validation")
    print("✅ FastAPI automatic documentation at /docs")
    print("✅ Environment variable security for API keys")
    print()
    print("📸 For LinkedIn Post:")
    print("1. Open http://localhost:8000/docs")
    print("2. Find POST /api/tts endpoint") 
    print("3. Click 'Try it out'")
    print("4. Test with sample data and take screenshot!")
    print()
    print("🔮 Ready for Day 3!")

if __name__ == "__main__":
    demo_tts_endpoint()