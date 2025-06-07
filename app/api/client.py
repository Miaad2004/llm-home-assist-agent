import requests
import json
from typing import Optional, Dict, Any


class SmartHomeAPIClient:
    """
    Client for interacting with the Smart Home Assistant REST API.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client.
        
        Args:
            base_url (str): Base URL of the API server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the API is running and healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"status": "error", "message": f"Connection error: {str(e)}"}
    
    def chat(self, message: str, use_tools: bool = True) -> Dict[str, Any]:
        """
        Send a message to the assistant and get a response.
        
        Args:
            message (str): The message to send
            use_tools (bool): Whether to use tools in the response
            
        Returns:
            Dict containing the response and status
        """
        try:
            payload = {
                "message": message,
                "use_tools": use_tools
            }
            response = self.session.post(f"{self.base_url}/chat", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"response": f"Error: {str(e)}", "status": "error"}
    
    def direct_llm_chat(self, message: str) -> Dict[str, Any]:
        """
        Send a message directly to the LLM without using tools.
        
        Args:
            message (str): The message to send
            
        Returns:
            Dict containing the response and status
        """
        try:
            payload = {"message": message}
            response = self.session.post(f"{self.base_url}/llm/direct", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"response": f"Error: {str(e)}", "status": "error"}
    
    def update_system_prompt(self, system_prompt: str) -> Dict[str, Any]:
        """
        Update the system prompt for the LLM.
        
        Args:
            system_prompt (str): The new system prompt
            
        Returns:
            Dict containing the status
        """
        try:
            payload = {"system_prompt": system_prompt}
            response = self.session.post(f"{self.base_url}/llm/system-prompt", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    def get_system_prompt(self) -> Dict[str, Any]:
        """Get the current system prompt."""
        try:
            response = self.session.get(f"{self.base_url}/llm/system-prompt")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    def clear_history(self) -> Dict[str, Any]:
        """Clear the conversation history."""
        try:
            response = self.session.post(f"{self.base_url}/llm/clear-history")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    def get_history(self) -> Dict[str, Any]:
        """Get the conversation history."""
        try:
            response = self.session.get(f"{self.base_url}/llm/history")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get a list of available tools."""
        try:
            response = self.session.get(f"{self.base_url}/tools")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    def reinitialize_agent(self) -> Dict[str, Any]:
        """Reinitialize the agent."""
        try:
            response = self.session.post(f"{self.base_url}/agent/reinitialize")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"status": "error", "message": f"Error: {str(e)}"}


def main():
    """
    Simple example of using the API client.
    """
    client = SmartHomeAPIClient()
    
    # Check health
    print("🔍 Checking API health...")
    health = client.health_check()
    print(f"Health: {health}")
    
    if health.get("status") != "healthy":
        print("❌ API is not healthy. Make sure the server is running.")
        return
    
    # Test chat
    print("\n💬 Testing chat...")
    response = client.chat("Hello! What's the weather like today?")
    print(f"Response: {response}")
    
    # Test direct LLM
    print("\n🤖 Testing direct LLM...")
    response = client.direct_llm_chat("Tell me a joke")
    print(f"Response: {response}")
    
    # Get available tools
    print("\n🛠️ Getting available tools...")
    tools = client.get_available_tools()
    print(f"Tools: {tools}")


if __name__ == "__main__":
    main()