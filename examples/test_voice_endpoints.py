#!/usr/bin/env python3
"""
Test script for the TTS and STT endpoints in the Smart Home Assistant API.
"""

import requests
import json
import io
import tempfile
import os

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    print("🏥 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_tts_synthesis():
    """Test text-to-speech synthesis."""
    print("🗣️ Testing TTS synthesis...")
    
    # Test data
    tts_request = {
        "text": "Hello, this is a test of the text-to-speech functionality in the smart home assistant.",
        "voice": "default"
    }
    
    response = requests.post(f"{BASE_URL}/tts/synthesize", json=tts_request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_tts_file_synthesis():
    """Test text-to-speech synthesis with file download."""
    print("📁 Testing TTS file synthesis...")
    
    # Test data
    tts_request = {
        "text": "This is a file download test for TTS.",
        "voice": "default"
    }
    
    response = requests.post(f"{BASE_URL}/tts/synthesize/file", json=tts_request)
    print(f"Status: {response.status_code}")
    print(f"Content Type: {response.headers.get('content-type', 'Unknown')}")
    print(f"Content Length: {len(response.content)} bytes")
    
    # Save the file for inspection
    if response.status_code == 200:
        with open("test_tts_output.txt", "wb") as f:
            f.write(response.content)
        print("✅ TTS file saved as 'test_tts_output.txt'")
    print()

def test_stt_transcription():
    """Test speech-to-text transcription with a dummy audio file."""
    print("🎤 Testing STT transcription...")
    
    # Create a dummy audio file for testing
    dummy_audio_content = b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"  # Minimal WAV header
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file.write(dummy_audio_content)
        temp_file_path = temp_file.name
    
    try:
        # Send the file to the STT endpoint
        with open(temp_file_path, "rb") as audio_file:
            files = {"audio_file": ("test_audio.wav", audio_file, "audio/wav")}
            response = requests.post(f"{BASE_URL}/stt/transcribe", files=files)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    print()

def test_live_stt():
    """Test live speech-to-text transcription."""
    print("🎙️ Testing live STT...")
    
    response = requests.post(f"{BASE_URL}/stt/live")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_voice_chat():
    """Test complete voice chat functionality."""
    print("💬 Testing voice chat (STT + Chat + TTS)...")
    
    # Create a dummy audio file for testing
    dummy_audio_content = b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file.write(dummy_audio_content)
        temp_file_path = temp_file.name
    
    try:
        with open(temp_file_path, "rb") as audio_file:
            files = {"audio_file": ("voice_message.wav", audio_file, "audio/wav")}
            response = requests.post(f"{BASE_URL}/voice/chat", files=files)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    print()

def test_available_tools():
    """Test getting available tools."""
    print("🔧 Testing available tools...")
    
    response = requests.get(f"{BASE_URL}/tools")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Number of tools: {data.get('count', 0)}")
        for tool in data.get('tools', [])[:3]:  # Show first 3 tools
            print(f"  - {tool['name']}: {tool['description']}")
    print()

def main():
    """Run all tests."""
    print("🚀 Testing Smart Home Assistant Voice Endpoints")
    print("=" * 60)
    
    try:
        test_health_check()
        test_tts_synthesis()
        test_tts_file_synthesis()
        test_stt_transcription()
        test_live_stt()
        test_voice_chat()
        test_available_tools()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    main()
