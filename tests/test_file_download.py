#!/usr/bin/env python3
"""
Test script for the new file download functionality
"""

import requests
import os
import tempfile
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows compatibility
init(autoreset=True)

BASE_URL = "http://localhost:8000"

def test_file_download_system():
    """Test the complete file download system."""
    print(f"{Fore.CYAN}Testing File Download System{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    
    # Step 1: Generate a TTS file
    print(f"{Fore.YELLOW}1. Generating TTS file...{Style.RESET_ALL}")
    tts_request = {
        "text": "This is a test of the file download system for TTS.",
        "voice": "default"
    }
    
    response = requests.post(f"{BASE_URL}/tts/synthesize", json=tts_request)
    if response.status_code != 200:
        print(f"{Fore.RED}TTS generation failed: {response.status_code}{Style.RESET_ALL}")
        return
    
    data = response.json()
    file_path = data.get("audio_file_path")
    print(f"{Fore.GREEN}TTS file generated: {file_path}{Style.RESET_ALL}")
    
    # Step 2: Test generic file download endpoint
    print(f"\n{Fore.YELLOW}2. Testing file download endpoint...{Style.RESET_ALL}")
    download_response = requests.get(f"{BASE_URL}/files/download", params={"file_path": file_path})
    
    if download_response.status_code != 200:
        print(f"{Fore.RED}File download failed: {download_response.status_code}{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}File downloaded successfully!{Style.RESET_ALL}")
    print(f"{Fore.BLUE}   Content-Type: {download_response.headers.get('content-type')}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}   Content-Length: {len(download_response.content)} bytes{Style.RESET_ALL}")
    print(f"{Fore.BLUE}   Content-Disposition: {download_response.headers.get('content-disposition')}{Style.RESET_ALL}")
    
    # Step 3: Save the downloaded file for verification
    downloaded_filename = "test_downloaded_file.wav"
    with open(downloaded_filename, "wb") as f:
        f.write(download_response.content)
    print(f"{Fore.GREEN}File saved as: {downloaded_filename}{Style.RESET_ALL}")
    
    # Step 4: Test file not found scenario
    print(f"\n{Fore.YELLOW}3. Testing error handling...{Style.RESET_ALL}")
    error_response = requests.get(f"{BASE_URL}/files/download", params={"file_path": "/nonexistent/file.txt"})
    if error_response.status_code == 404:
        print(f"{Fore.GREEN}Error handling works - 404 for non-existent file{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Unexpected response for non-existent file: {error_response.status_code}{Style.RESET_ALL}")
    
    print(f"\n{Fore.MAGENTA}File download system test completed!{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        test_file_download_system()
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}Cannot connect to API server. Make sure it's running at http://localhost:8000{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Test failed with error: {e}{Style.RESET_ALL}")
