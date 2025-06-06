# Test script for WebViewer

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from data.web_viewer import WebViewer

def test_web_viewer():
    """Test the WebViewer functionality."""
    web_viewer = WebViewer()
    
    # Test basic webpage viewing
    print("Testing webpage viewing...")
    result = web_viewer.view_webpage("https://httpbin.org/html", max_content_length=1000)
    print(f"Status: {result['status']}")
    print(f"Title: {result['title']}")
    print(f"Content length: {len(result['content'])}")
    print(f"Number of links: {len(result['links'])}")
    print()
    
    # Test page summary
    print("Testing page summary...")
    summary = web_viewer.get_page_summary("https://httpbin.org/html")
    print(f"Summary: {summary}")
    print()
    
    # Test search in page
    print("Testing search in page...")
    search_result = web_viewer.search_in_page("https://httpbin.org/html", "html")
    print(f"Found: {search_result['found']}")
    print(f"Matches: {search_result['matches']}")
    if search_result['contexts']:
        print(f"First context: {search_result['contexts'][0]}")
    print()

if __name__ == "__main__":
    test_web_viewer()
