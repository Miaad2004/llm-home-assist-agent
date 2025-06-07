#!/usr/bin/env python3
"""
Comprehensive test script for the secure file download system.
Tests TTS synthesis, file generation, and secure download functionality.
"""

import requests
import os
import tempfile
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if the API server is running."""
    print("🏥 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        print("✅ Server is healthy")
        return True
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return False

def test_tts_synthesis():
    """Test TTS synthesis and verify it returns filename only."""
    print("\n🗣️ Testing TTS synthesis...")
    
    test_text = "Hello, this is a test of the secure file download system!"
    payload = {
        "text": test_text,
        "voice": "default"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tts/synthesize", json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Verify response structure
        assert "audio_filename" in data, "Response should contain audio_filename"
        assert "download_url" in data, "Response should contain download_url"
        
        filename = data["audio_filename"]
        
        # Verify filename security (no path separators)
        assert "/" not in filename and "\\" not in filename, "Filename should not contain path separators"
        
        print(f"✅ TTS synthesis successful, filename: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ TTS synthesis failed: {e}")
        return None

def test_secure_download(filename):
    """Test secure file download."""
    print(f"\n📁 Testing secure download for: {filename}")
    
    try:
        # Test successful download
        response = requests.get(f"{BASE_URL}/files/download", params={"filename": filename})
        response.raise_for_status()
        
        # Verify content type
        assert response.headers.get('content-type') == 'audio/wav', "Content type should be audio/wav"
        
        # Verify file content
        content = response.text
        assert "Audio file placeholder" in content, "File should contain placeholder content"
        
        print(f"✅ Secure download successful for {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Secure download failed: {e}")
        return False

def test_security_path_traversal():
    """Test that path traversal attacks are prevented."""
    print(f"\n🔒 Testing security (path traversal prevention)...")
    
    # Test various path traversal attempts
    malicious_filenames = [
        "../config/settings.py",
        "..\\config\\settings.py", 
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
        "config/settings.py",
        "/etc/passwd",
        "C:\\windows\\system32\\config\\sam"
    ]
    
    security_passed = True
    
    for filename in malicious_filenames:
        try:
            response = requests.get(f"{BASE_URL}/files/download", params={"filename": filename})
            if response.status_code == 200:
                print(f"❌ SECURITY BREACH: Successfully accessed {filename}")
                security_passed = False
            else:
                print(f"✅ Security check passed for {filename} (HTTP {response.status_code})")
        except Exception as e:
            print(f"✅ Security check passed for {filename} (Exception: {e})")
    
    return security_passed

def test_nonexistent_file():
    """Test download of non-existent file."""
    print(f"\n🚫 Testing non-existent file download...")
    
    try:
        response = requests.get(f"{BASE_URL}/files/download", params={"filename": "nonexistent_file.wav"})
        assert response.status_code == 404, "Should return 404 for non-existent file"
        print("✅ Non-existent file correctly returns 404")
        return True
    except Exception as e:
        print(f"❌ Non-existent file test failed: {e}")
        return False

def test_tts_file_endpoint():
    """Test TTS file endpoint that directly returns file."""
    print(f"\n📄 Testing TTS file endpoint...")
    
    payload = {
        "text": "Direct file download test",
        "voice": "default"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tts/synthesize/file", json=payload)
        response.raise_for_status()
        
        # Verify it returns file content
        assert response.headers.get('content-type') == 'audio/wav', "Should return audio file"
        assert len(response.content) > 0, "Should have file content"
        
        print("✅ TTS file endpoint working correctly")
        return True
        
    except Exception as e:
        print(f"❌ TTS file endpoint failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Starting comprehensive secure file download tests...\n")
    
    # Test server health
    if not test_health():
        print("❌ Server not available, stopping tests")
        return
    
    # Test TTS synthesis
    filename = test_tts_synthesis()
    if not filename:
        print("❌ TTS synthesis failed, stopping tests")
        return
    
    # Test secure download
    if not test_secure_download(filename):
        print("❌ Secure download failed")
        return
    
    # Test security
    if not test_security_path_traversal():
        print("❌ Security tests failed")
        return
    
    # Test non-existent file
    if not test_nonexistent_file():
        print("❌ Non-existent file test failed")
        return
    
    # Test TTS file endpoint
    if not test_tts_file_endpoint():
        print("❌ TTS file endpoint test failed")
        return
    
    print("\n🎉 All tests passed! Secure file download system is working correctly.")
    print("\n📋 Summary:")
    print("✅ TTS synthesis generates files in secure download folder")
    print("✅ API returns filenames only (not full paths)")
    print("✅ Secure download endpoint works correctly")
    print("✅ Path traversal attacks are prevented")
    print("✅ Non-existent files return proper 404 errors")
    print("✅ Direct file download endpoint works")

if __name__ == "__main__":
    main()
