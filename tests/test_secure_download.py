#!/usr/bin/env python3
"""
Test script for the secure file download system.
Tests both valid downloads and security restrictions.
"""

import requests
import tempfile
import os
import sys

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

BASE_URL = "http://localhost:8000"

def test_tts_synthesis_and_download():
    """Test TTS synthesis and secure file download."""
    print("🎵 Testing TTS synthesis and secure download...")
    
    # Test TTS synthesis
    tts_request = {
        "text": "This is a secure file download test.",
        "voice": "default"
    }
    
    response = requests.post(f"{BASE_URL}/tts/synthesize", json=tts_request)
    print(f"TTS Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"TTS Response: {data}")
        
        # Extract filename from response
        audio_filename = data.get('audio_filename')
        if audio_filename:
            print(f"Audio filename: {audio_filename}")
            
            # Test secure download
            download_response = requests.get(f"{BASE_URL}/files/download", 
                                           params={"filename": audio_filename})
            print(f"Download Status: {download_response.status_code}")
            
            if download_response.status_code == 200:
                print(f"✅ Download successful! Content-Type: {download_response.headers.get('content-type')}")
                print(f"Content-Length: {len(download_response.content)} bytes")
            else:
                print(f"❌ Download failed: {download_response.text}")
        else:
            print("❌ No filename in TTS response")
    else:
        print(f"❌ TTS failed: {response.text}")
    print()

def test_security_restrictions():
    """Test security restrictions on file downloads."""
    print("🔒 Testing security restrictions...")
    
    # Test 1: Try to access file with path traversal
    print("Test 1: Path traversal attack")
    response = requests.get(f"{BASE_URL}/files/download", 
                           params={"filename": "../config/settings.py"})
    print(f"Status: {response.status_code} (should be 400)")
    if response.status_code == 400:
        print("✅ Path traversal blocked")
    else:
        print("❌ Security vulnerability!")
    
    # Test 2: Try to access file with absolute path
    print("Test 2: Absolute path")
    response = requests.get(f"{BASE_URL}/files/download", 
                           params={"filename": "/etc/passwd"})
    print(f"Status: {response.status_code} (should be 400)")
    if response.status_code == 400:
        print("✅ Absolute path blocked")
    else:
        print("❌ Security vulnerability!")
    
    # Test 3: Try to access non-existent file
    print("Test 3: Non-existent file")
    response = requests.get(f"{BASE_URL}/files/download", 
                           params={"filename": "nonexistent.txt"})
    print(f"Status: {response.status_code} (should be 404)")
    if response.status_code == 404:
        print("✅ Non-existent file properly handled")
    else:
        print("❌ Unexpected response!")
    
    print()

def test_file_upload_and_download():
    """Test creating a file in downloads folder and downloading it."""
    print("📂 Testing file creation and download...")
    
    from config.settings import Settings
    
    # Create a test file in the downloads folder
    download_folder = Settings.DOWNLOAD_FOLDER_PATH
    os.makedirs(download_folder, exist_ok=True)
    
    test_filename = "test_secure_download.txt"
    test_filepath = os.path.join(download_folder, test_filename)
    test_content = "This is a test file for secure download functionality."
    
    with open(test_filepath, 'w') as f:
        f.write(test_content)
    
    print(f"Created test file: {test_filename}")
    
    # Test download
    response = requests.get(f"{BASE_URL}/files/download", 
                           params={"filename": test_filename})
    print(f"Download Status: {response.status_code}")
    
    if response.status_code == 200:
        downloaded_content = response.text
        if downloaded_content == test_content:
            print("✅ File downloaded correctly!")
        else:
            print("❌ Downloaded content doesn't match!")
    else:
        print(f"❌ Download failed: {response.text}")
    
    # Clean up
    try:
        os.remove(test_filepath)
        print("Test file cleaned up")
    except:
        pass
    
    print()

def main():
    print("🧪 Testing Secure File Download System")
    print("=====================================\n")
    
    try:
        # Check if API is running
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ API is not responding correctly")
            return
        print("✅ API is running\n")
        
        # Run tests
        test_tts_synthesis_and_download()
        test_security_restrictions()
        test_file_upload_and_download()
        
        print("🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
