#!/usr/bin/env python3
"""
Demo script showing how to interact with the Smart Home Assistant API.
"""

import sys
import os
import time

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.api.client import SmartHomeAPIClient


def main():
    """Demonstrate API functionality."""
    print("🏠 Smart Home Assistant API Demo")
    print("=" * 50)
    
    # Initialize the client
    client = SmartHomeAPIClient()
    
    # 1. Health check
    print("\n1️⃣ Health Check")
    print("-" * 20)
    health = client.health_check()
    print(f"Status: {health.get('status', 'unknown')}")
    print(f"Message: {health.get('message', 'No message')}")
    
    if health.get("status") != "healthy":
        print("❌ API is not healthy. Please start the server first using:")
        print("   PowerShell: .\\start_api.ps1")
        print("   Python: python scripts/start_api.py")
        return
    
    # 2. Get available tools
    print("\n2️⃣ Available Tools")
    print("-" * 20)
    tools = client.get_available_tools()
    if tools.get("status") == "success":
        print(f"Found {tools.get('count', 0)} tools:")
        for tool in tools.get("tools", []):
            print(f"  • {tool.get('name', 'Unknown')}")
    else:
        print(f"Error: {tools.get('message', 'Unknown error')}")
    
    # 3. Test direct LLM chat (simple conversation)
    print("\n3️⃣ Direct LLM Chat")
    print("-" * 20)
    response = client.direct_llm_chat("Hello! Please introduce yourself briefly.")
    if response.get("status") == "success":
        print(f"LLM: {response.get('response', 'No response')}")
    else:
        print(f"Error: {response.get('response', 'Unknown error')}")
    
    # 4. Test smart chat with tools
    print("\n4️⃣ Smart Chat with Tools")
    print("-" * 20)
    test_queries = [
        "What time is it?",
        "What's the weather like in New York?",
        "Search for the latest AI news"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        response = client.chat(query)
        if response.get("status") == "success":
            print(f"✅ Response: {response.get('response', 'No response')[:200]}...")
        else:
            print(f"❌ Error: {response.get('response', 'Unknown error')}")
        time.sleep(1)  # Small delay between requests
    
    # 5. Test system prompt management
    print("\n5️⃣ System Prompt Management")
    print("-" * 20)
    
    # Get current system prompt
    current_prompt = client.get_system_prompt()
    if current_prompt.get("status") == "success":
        print(f"Current prompt: {current_prompt.get('system_prompt', 'None')[:100]}...")
    
    # Update system prompt
    new_prompt = "You are a helpful assistant that always responds with enthusiasm and uses emojis! 🎉"
    update_result = client.update_system_prompt(new_prompt)
    if update_result.get("status") == "success":
        print("✅ System prompt updated successfully!")
        
        # Test with new prompt
        response = client.direct_llm_chat("Tell me about yourself.")
        if response.get("status") == "success":
            print(f"New style response: {response.get('response', 'No response')}")
    
    # 6. Test conversation history
    print("\n6️⃣ Conversation History")
    print("-" * 20)
    history = client.get_history()
    if history.get("status") == "success":
        print(f"Conversation has {len(history.get('history', []))} messages")
        
        # Clear history
        clear_result = client.clear_history()
        if clear_result.get("status") == "success":
            print("✅ History cleared successfully!")
    
    print("\n🎉 Demo completed! The API is working correctly.")
    print("💡 You can now use the API endpoints in your applications.")
    print("📖 Check http://localhost:8000/docs for interactive API documentation.")


if __name__ == "__main__":
    main()