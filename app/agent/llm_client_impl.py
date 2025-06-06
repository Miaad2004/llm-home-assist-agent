from .llm_client import LLMClientInterface
import openai
from typing import Dict, List, Any, Union

class GenericOpenAILLMClient(LLMClientInterface):
    """
    Generic LLM client implementation using the openai library.
    Can be configured for any LLM endpoint supported by openai.
    """
    def __init__(self, api_key: str, model: str, api_base: str = "", system_prompt_path: str = ""):
        """
        api_key: str — API key for the LLM provider
        model: str — Model name (e.g., "gpt-3.5-turbo", "groq/model", "togetherai/model")
        api_base: str — Optional custom API endpoint
        """
        self.api_key = api_key
        self.model = model
        self.api_base = api_base or None
        self.system_prompt = open(system_prompt_path, 'r').read() if system_prompt_path else ""
        self.history = [{"role": "system", "content": self.system_prompt}] if self.system_prompt else []
        
        openai.api_key = self.api_key
        if self.api_base:
            openai.base_url = self.api_base

    def send_prompt(self, prompt: str) -> str:
        """
        Input: str — Prompt
        Output: str — LLM response
        Calls: openai.resources.chat.completions.create (openai>=1.0.0)
        """

        try:
            self.history.append({"role": "user", "content": prompt})
            response = openai.chat.completions.create(
                model=self.model,
                messages=self.history
            )
            
            self.history.append({"role": "assistant", "content": response.choices[0].message.content})
            return response.choices[0].message.content
        
        except Exception as e:
            return f"[Error] {str(e)}"
            
    def send_prompt_with_functions(self, messages: List[Dict[str, str]], functions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Input: 
            messages: List[Dict[str, str]] — Conversation messages
            functions: List[Dict[str, Any]] — Function definitions
        Output: Dict[str, Any] — Response from LLM with possible function calls
        Called by: DeviceCommandAgentImpl.handle_user_input()
        Calls: External LLM API with function calling enabled
        """
        openai.api_key = self.api_key
        if self.api_base:
            openai.base_url = self.api_base
            
        try:
            # Convert functions to OpenAI's format
            tools = [{"type": "function", "function": func} for func in functions]
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Create a response dictionary that includes function call info if present
            result = {"content": message.content or ""}
            
            # Check if function call was made
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_call = {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
                result["function_call"] = function_call
                
            return result
            
        except Exception as e:
            return {"content": f"[Error] {str(e)}"}
