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
    def __init__(self, api_key: str="", model: str="", api_base: str = "", temperature: float = None):
        """
        Initializes the client.
        
        Args:
            api_key (str): API key for the LLM provider.
            model (str): Model name (e.g., "llama-3.1-8b-instant").
            api_base (str): Optional custom API endpoint.
            temperature (float): Controls randomness in the model's output (0.0-2.0).
        """
        if not temperature:
            self.temperature = getattr(Settings, 'LLM_TEMPERATURE', 0.7)  # Default to 0.7 if not provided
        
        self.api_key = api_key or Settings.LLM_API_KEY
        if not self.api_key:
            raise ValueError("API key must be provided.")
        
        self.model = model or Settings.LLM_MODEL
        if not self.model:
            raise ValueError("Model name must be provided.")
        
        self.api_base = api_base or Settings.LLM_API_ENDPOINT or None
        self.temperature = temperature if temperature is not None else getattr(Settings, 'LLM_TEMPERATURE', 0.7)
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
            
    def clear_hist(self):
        """
        Clears the conversation history, preserving the system prompt if set.
        """
        self.history = [{"role": "system", "content": self.system_prompt}] if self.system_prompt else []

    def send_prompt(self, prompt, tools: Optional[List[Dict[str, Any]]] = None, tool_choice: Optional[str] = None) -> Any:
        """
        Sends a prompt to the LLM and returns the response.
        
        Args:
            prompt (str): The user input prompt.
            tools (List[Dict[str, Any]], optional): List of tool definitions.
            tool_choice (str, optional): Control whether the model can use tools. 
                                         Options: "auto", "required", "none".
        
        Returns:
            Any: The LLM's response, either as a string or a message object with tool calls.
        """        
        try:
            # Only add user message if prompt is not empty
            # For continued tool conversations, the history already contains the necessary context
            if prompt and prompt.strip():
                self.history.append({"role": "user", "content": prompt})
            
            # Create request parameters
            request_params = {
                "model": self.model,
                "messages": self.history,
                "temperature": self.temperature
            }
            
            # Add tools if provided
            if tools:
                request_params["tools"] = tools
                # Set tool_choice based on parameter, default to "auto" if not specified
                request_params["tool_choice"] = tool_choice if tool_choice else "auto"

            # Print the request parameters before sending
            print(f"{Fore.GREEN}{'=' * 60}")
            print(f"{Fore.BLUE}{Style.BRIGHT}📤 LLM REQUEST")
            print(f"{Fore.GREEN}{'=' * 60}")
            try:
                req_json_str = json.dumps(request_params, indent=2, ensure_ascii=False, default=str)
                import re
                # Highlight all dictionary keys in magenta
                req_json_str = re.sub(r'"([^"]+)":', f'{Fore.MAGENTA}"\\1"{Fore.WHITE}:', req_json_str)
                # Highlight string values in green
                req_json_str = re.sub(r'": "([^"]*)"', f'": {Fore.GREEN}"\\1"{Style.RESET_ALL}', req_json_str)
                # Highlight numbers in yellow
                req_json_str = re.sub(r'": (\d+)', f'": {Fore.YELLOW}\\1{Style.RESET_ALL}', req_json_str)
                # Highlight booleans in blue
                req_json_str = re.sub(r'": (true|false|null)', f'": {Fore.BLUE}\\1{Style.RESET_ALL}', req_json_str)
                print(f"{Fore.WHITE}{req_json_str}")
                
            except Exception as req_err:
                print(f"{Fore.WHITE}{request_params}")
                
            print(f"{Fore.GREEN}{'=' * 60}{Style.RESET_ALL}")

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
            
            history_message_to_add = None

            # Check if the response includes structured tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # Directly modify message.tool_calls to ensure IDs are non-empty
                # This ensures agent_impl.py receives the corrected IDs via the returned message object.
                for i, tc in enumerate(message.tool_calls):
                    if not tc.id or not tc.id.strip():
                        new_id = f"generated_tc_id_{i}"
                        print(f"{Fore.YELLOW}Warning: LLM returned tool_call with empty ID. Replacing with '{new_id}'.{Style.RESET_ALL}")
                        tc.id = new_id # Modify the id on the tool_call object itself
                    
                    # Ensure function name is present (it was in the log, but good practice)
                    if not hasattr(tc, 'function') or not getattr(tc.function, 'name', None):
                         print(f"{Fore.RED}Error: LLM tool_call missing function name for id '{tc.id}'.{Style.RESET_ALL}")
                         # This tool call might be problematic for execution and history.

                # Now that message.tool_calls has corrected IDs, use it for history
                history_message_to_add = {"role": "assistant", "tool_calls": message.tool_calls}
                
                # Add content if it exists (e.g., assistant speaks then calls tool)
                if message.content and message.content.strip():
                    history_message_to_add["content"] = message.content
            
            # Fallback: Check if tool calls are embedded in the content as text 
            # This block is largely unchanged but is secondary to the structured tool_calls handling.
            # If this path is taken, it implies the LLM is not returning structured tool_calls,
            # and this code would also need to ensure its `history_message_to_add` is correct
            # and that `message.tool_calls` is populated for agent_impl.py.
            elif message.content and "[tool_calls]:" in message.content:
                try:
                    # Extract the tool calls from the content
                    import re
                    import ast
                    
                    # Find the tool_calls part in the content
                    tool_calls_match = re.search(r'\[tool_calls\]:\s*(\[.*\])', message.content, re.DOTALL)
                    if tool_calls_match:
                        tool_calls_str = tool_calls_match.group(1)
                        
                        # Try to parse as JSON first, then fallback to ast.literal_eval
                        try:
                            tool_calls_data = json.loads(tool_calls_str)
                        except json.JSONDecodeError:
                            tool_calls_data = ast.literal_eval(tool_calls_str)
                        
                        # Create a mock message object with tool calls
                        # This part of the original code was creating a mock message but not fully integrating it
                        # for history in the new required format or for agent_impl.
                        # For now, if this path is hit, it will likely still have issues.
                        # The primary fix is for the structured `message.tool_calls` path.
                        print(f"{Fore.YELLOW}Warning: Tool calls parsed from string content. History format for this path may need review.{Style.RESET_ALL}")
                        
                        # For history, we'd need to structure it like the primary path:
                        parsed_tool_calls_for_history = []
                        for i, raw_tc in enumerate(tool_calls_data):
                            tc_id = raw_tc.get('id')
                            if not tc_id or not tc_id.strip():
                                tc_id = f"parsed_fallback_id_{i}"
                            parsed_tool_calls_for_history.append({
                                "id": tc_id,
                                "type": raw_tc.get('type', 'function'),
                                "function": raw_tc.get('function', {}) # Ensure name/args are present
                            })
                        
                        if parsed_tool_calls_for_history:
                            history_message_to_add = {"role": "assistant", "tool_calls": parsed_tool_calls_for_history}
                            main_content = message.content.split("[tool_calls]:")[0].strip()
                            if main_content:
                                history_message_to_add["content"] = main_content
                            
                            # To make agent_impl.py work, message.tool_calls would need to be populated.
                            # This is complex to do robustly here.
                            # For now, this path remains less robust.
                            
                        # The original code created a MockMessage and returned it.
                        # This was problematic as it wasn't the full response object.
                        # We will let `message` be returned, but its `tool_calls` attribute
                        # won't be populated if we came through this string parsing path without modifying `message`.

                    else: # No match for [tool_calls] structure, treat as plain content
                        if message.content:
                            history_message_to_add = {"role": "assistant", "content": message.content}
                    
                except Exception as parse_error:
                    print(f"{Fore.RED}❌ Error parsing tool calls from content: {parse_error}{Style.RESET_ALL}")
                    if message.content: # Fallback to treating as regular content
                         history_message_to_add = {"role": "assistant", "content": message.content}
            
            # If no tool calls were processed (neither structured nor parsed from string),
            # and there's content, then it's a simple content message.
            elif message.content: # Ensure this is elif, not if, to avoid double-adding content
                 history_message_to_add = {"role": "assistant", "content": message.content}

            # Add to history if a message was constructed
            if history_message_to_add:
                self.history.append(history_message_to_add)
            # If history_message_to_add is None (e.g. empty response from LLM), nothing is added.
            
            return message # Return the original (potentially modified for tc.id) message object
        
        except Exception as e:
            print(f"{Fore.RED}❌ LLM error: {e}{Style.RESET_ALL}")
            return f"[Error] {str(e)}"