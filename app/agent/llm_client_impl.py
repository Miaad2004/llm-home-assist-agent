from .llm_client import LLMClientInterface
import openai
from typing import Dict, List, Any, Union, Optional
from config.settings import Settings
import json
from colorama import Fore, Back, Style, init

# Initialize colorama for Windows compatibility
init(autoreset=True)

class GenericLLMClient(LLMClientInterface):
    """
    A client for interacting with OpenAI's LLMs.
    """
    def __init__(self, api_key: str="", model: str="", api_base: str = ""):
        """
        Initializes the client.
        
        Args:
            api_key (str): API key for the LLM provider.
            model (str): Model name (e.g., "llama-3.1-8b-instant").
            api_base (str): Optional custom API endpoint.
        """
        self.api_key = api_key or Settings.LLM_API_KEY
        if not self.api_key:
            raise ValueError("API key must be provided.")
        
        self.model = model or Settings.LLM_MODEL
        if not self.model:
            raise ValueError("Model name must be provided.")
        
        self.api_base = api_base or Settings.LLM_API_ENDPOINT or None
        self.system_prompt = ""
        self.history = [{"role": "system", "content": self.system_prompt}] if self.system_prompt else []
        
        openai.api_key = self.api_key
        if self.api_base:
            openai.base_url = self.api_base

    def update_system_prompt(self, system_prompt: str):
        """
        Updates the system prompt.
        
        Args:
            system_prompt (str): The new system prompt.
        """
        self.system_prompt = system_prompt
        if self.history and self.history[0]["role"] == "system":
            self.history[0]["content"] = system_prompt
        else:
            self.history = [{"role": "system", "content": system_prompt}] + self.history
    
    def send_prompt(self, prompt: str, tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        """
        Sends a prompt to the LLM and returns the response.
        
        Args:
            prompt (str): The user input prompt.
            tools (List[Dict[str, Any]], optional): List of tool definitions.
        
        Returns:
            Any: The LLM's response, either as a string or a message object with tool calls.
        """
        try:
            if prompt:
                self.history.append({"role": "user", "content": prompt})
            
            # Create request parameters
            request_params = {
                "model": self.model,
                "messages": self.history
            }
            
            # Add tools if provided
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            response = openai.chat.completions.create(**request_params)
            
            # Prettify the LLM response output with colors
            print(f"{Fore.CYAN}{'=' * 60}")
            print(f"{Fore.YELLOW}{Style.BRIGHT}🤖 LLM RESPONSE")
            print(f"{Fore.CYAN}{'=' * 60}")
            try:
                # Convert response to dict and pretty print with syntax highlighting
                response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
                json_str = json.dumps(response_dict, indent=2, ensure_ascii=False)
                
                # Highlight all dictionary keys in magenta
                import re
                json_str = re.sub(r'"([^"]+)":', f'{Fore.MAGENTA}"\\1"{Fore.WHITE}:', json_str)
                
                # Highlight string values in green
                json_str = re.sub(r'": "([^"]*)"', f'": {Fore.GREEN}"\\1"{Style.RESET_ALL}', json_str)
                
                # Highlight numbers in yellow
                json_str = re.sub(r'": (\d+)', f'": {Fore.YELLOW}\\1{Style.RESET_ALL}', json_str)
                
                # Highlight booleans in blue
                json_str = re.sub(r'": (true|false|null)', f'": {Fore.BLUE}\\1{Style.RESET_ALL}', json_str)
                
                print(f"{Fore.WHITE}{json_str}")
            except Exception as color_error:
                # Fallback to string representation with basic coloring
                print(f"{Fore.WHITE}{response}")
            print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
            
            # Get the message content
            message = response.choices[0].message
            
            # Check if the response includes tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # Add assistant message with tool calls to history (store tool_calls as string in content for compatibility)
                self.history.append({
                    "role": "assistant",
                    "content": (message.content or "") + "\n[tool_calls]: " + str([
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in message.tool_calls
                    ])
                })
                return message
            else:
                # Add assistant message to history
                self.history.append({"role": "assistant", "content": message.content})
                return message.content
        
        except Exception as e:
            print(f"{Fore.RED}❌ LLM error: {e}{Style.RESET_ALL}")
            return f"[Error] {str(e)}"