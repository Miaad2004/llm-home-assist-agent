#!/usr/bin/env python3
"""
Test script for the new file download functionality
"""

import requests
import os
import tempfile

BASE_URL = "http://localhost:8000"

def test_file_download_system():
    """Test the complete file download system."""
    print("🧪 Testing File Download System")
    print("=" * 50)
    
    # Step 1: Generate a TTS file
    print("1. Generating TTS file...")
    tts_request = {
        "text": "This is a test of the file download system for TTS.",
        "voice": "default"
    }
    
    response = requests.post(f"{BASE_URL}/tts/synthesize", json=tts_request)
    if response.status_code != 200:
        print(f"❌ TTS generation failed: {response.status_code}")
        return
    
    data = response.json()
    file_path = data.get("audio_file_path")
    print(f"✅ TTS file generated: {file_path}")
    
    # Step 2: Test generic file download endpoint
    print("\n2. Testing file download endpoint...")
    download_response = requests.get(f"{BASE_URL}/files/download", params={"file_path": file_path})
    
    if download_response.status_code != 200:
        print(f"❌ File download failed: {download_response.status_code}")
        return
    
    print(f"✅ File downloaded successfully!")
    print(f"   Content-Type: {download_response.headers.get('content-type')}")
    print(f"   Content-Length: {len(download_response.content)} bytes")
    print(f"   Content-Disposition: {download_response.headers.get('content-disposition')}")
    
    # Step 3: Save the downloaded file for verification
    downloaded_filename = "test_downloaded_file.wav"
    with open(downloaded_filename, "wb") as f:
        f.write(download_response.content)
    print(f"✅ File saved as: {downloaded_filename}")
    
    # Step 4: Test file not found scenario
    print("\n3. Testing error handling...")
    error_response = requests.get(f"{BASE_URL}/files/download", params={"file_path": "/nonexistent/file.txt"})
    if error_response.status_code == 404:
        print("✅ Error handling works - 404 for non-existent file")
    else:
        print(f"❌ Unexpected response for non-existent file: {error_response.status_code}")
    
    print("\n🎉 File download system test completed!")

if __name__ == "__main__":
    try:
        test_file_download_system()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Make sure it's running at http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
