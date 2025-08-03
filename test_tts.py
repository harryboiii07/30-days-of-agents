#!/usr/bin/env python3
"""
Test script for Day 2 TTS endpoint
This script tests the new /api/tts endpoint functionality
"""

import requests
import json
import time

def test_tts_endpoint():
    """Test the TTS endpoint with sample text"""
    url = "http://localhost:8000/api/tts"
    
    # Test data
    test_data = {
        "text": "Hello! This is a test of the Murf TTS API integration for Day 2 of 30 Days of Voice Agents.",
        "voice_id": "en-US-sarah"
    }
    
    print("🎙️ Testing TTS Endpoint - Day 2")
    print("=" * 50)
    print(f"📝 Text: {test_data['text']}")
    print(f"🔊 Voice: {test_data['voice_id']}")
    print("\n🚀 Sending request to TTS endpoint...")
    
    try:
        response = requests.post(url, json=test_data, timeout=60)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ TTS Request Successful!")
            print(f"🎯 Success: {result.get('success')}")
            print(f"📝 Message: {result.get('message')}")
            
            if result.get('audio_url'):
                print(f"🎵 Audio URL: {result.get('audio_url')}")
                print("\n🎉 TTS endpoint is working correctly!")
            else:
                print("⚠️  No audio URL returned")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - TTS generation may take time")
    except requests.exceptions.RequestException as e:
        print(f"🔥 Network error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

def test_health_endpoint():
    """Test the health endpoint to verify server is running"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Server Status: {result.get('message')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

if __name__ == "__main__":
    print("🎙️ Day 2 TTS Endpoint Testing")
    print("=" * 40)
    
    # First check if server is running
    if test_health_endpoint():
        print("\n" + "=" * 40)
        test_tts_endpoint()
    else:
        print("\n❌ Server not responding. Please start the server first:")
        print("   source venv/bin/activate && python main.py")
    
    print("\n💡 Next steps:")
    print("   • Open http://localhost:8000/docs to test via Swagger UI")
    print("   • Use Postman to test the endpoint")
    print("   • Take a screenshot for your LinkedIn post!")