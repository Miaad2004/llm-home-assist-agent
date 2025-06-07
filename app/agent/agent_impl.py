from .base import DeviceCommandAgent, Response, ToolOutput
from .llm_client import LLMClientInterface

from config.settings import Settings
import json
import ast
from colorama import Fore, Style, init

init(autoreset=True)


class MyAgent(DeviceCommandAgent):
    def __init__(self, llm_client: LLMClientInterface, tools: dict, base_sys_prompt_path: str = "", device_control=None):
        """
        Initializes the agent with an LLM client, tools, and device controller.
        """
        print(f"{Fore.BLUE}{Style.BRIGHT}[AGENT INIT]{Style.RESET_ALL} {Fore.WHITE}Initializing MyAgent...")
        self.tools = tools
        self.llm_client = llm_client
        self.device_control = device_control

        # Hook up device controller to generic_tools
        if device_control is not None:
            try:
                import app.tools.generic_tools as generic_tools
                generic_tools.device_controller = device_control
                print(f"{Fore.BLUE}[AGENT INIT]{Style.RESET_ALL} {Fore.GREEN}Device controller hooked to generic_tools.")
            except ImportError as e:
                print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Could not import generic_tools to set device_controller: {e}")
        
        # Set a simpler system prompt - we don't need the complex tool instructions anymore
        system_prompt = "You are a helpful smart home assistant. You can control devices, check the weather, get news, and more."
        if base_sys_prompt_path:
            try:
                with open(base_sys_prompt_path, "r") as f:
                    custom_prompt = f.read()
                if custom_prompt:
                    system_prompt = custom_prompt
                print(f"{Fore.BLUE}[AGENT INIT]{Style.RESET_ALL} {Fore.GREEN}Loaded custom system prompt from {base_sys_prompt_path}.")
            except Exception as e:
                print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Could not load system prompt: {e}")
        
        self.llm_client.update_system_prompt(system_prompt)
        
        if Settings.VERBOSE_LEVEL > 1:
            print(f"System prompt: {system_prompt}")
    
    def _format_tools_for_api(self):
        """
        Formats the tools dictionary into the format expected by the OpenAI API.
        """
        formatted_tools = []
        for tool_name, tool_info in self.tools.items():
            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_info["description"],
                    "parameters": tool_info["parameters"]
                }
            })
        return formatted_tools
    
    def handle_user_input(self, user_text: str) -> str:
        """
        Processes user input and returns a response.
        Supports nested tool calls - the LLM can request multiple tools in sequence.
        """
        print(f"{Fore.CYAN}{Style.BRIGHT}[USER INPUT]{Style.RESET_ALL} {Fore.WHITE}{user_text}")
        # Format tools for the API
        formatted_tools = self._format_tools_for_api()
        
        # Send the initial prompt with tool definitions
        response = self.llm_client.send_prompt(user_text, tools=formatted_tools)
        
        # If response is a string, return it directly (no tool calls)
        if isinstance(response, str):
            print(f"{Fore.GREEN}{Style.BRIGHT}[AGENT RESPONSE]{Style.RESET_ALL} {Fore.WHITE}{response}")
            return response
        
        # Maximum number of tool call iterations to prevent infinite loops
        max_iterations = 5
        current_iteration = 0
        
        # Continue processing tool calls until we get a content response or hit max iterations
        while current_iteration < max_iterations:
            current_iteration += 1
            
            # Check if we have a content response (no more tool calls)
            if not hasattr(response, 'tool_calls') or not response.tool_calls:
                if hasattr(response, 'content') and response.content:
                    print(f"{Fore.GREEN}{Style.BRIGHT}[AGENT RESPONSE]{Style.RESET_ALL} {Fore.WHITE}{response.content}")
                    return response.content
                break
            
            # Process each tool call
            for tool_call in response.tool_calls:
                tool_name = tool_call.function.name
                
                try:
                    # Parse the arguments
                    args = json.loads(tool_call.function.arguments)
                    print(f"\n{Fore.CYAN}{'='*60}")
                    print(f"{Fore.YELLOW}{Style.BRIGHT}[TOOL CALL {current_iteration}]{Style.RESET_ALL} {Fore.WHITE}{tool_name} called with parameters:")
                    print(f"{Fore.GREEN}{json.dumps(args, indent=2)}")
                    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
                    
                    # Execute the tool
                    if tool_name in self.tools:
                        tool_function = self.tools[tool_name]["function"]
                        result = tool_function(**args)
                        print(f"{Fore.MAGENTA}{Style.BRIGHT}[TOOL RESPONSE]{Style.RESET_ALL} {Fore.WHITE}{tool_name} returned:")
                        if not isinstance(result, str):
                            print(f"{Fore.GREEN}{json.dumps(result, indent=2)}")
                        else:
                            print(f"{Fore.GREEN}{result}")
                        # Add the tool result to the conversation
                        self.llm_client.history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": str(result)
                        })
                    else:
                        error_msg = f"Error: Tool '{tool_name}' not found"
                        print(f"{Fore.RED}{Style.BRIGHT}[TOOL ERROR]{Style.RESET_ALL} {Fore.WHITE}{error_msg}")
                        self.llm_client.history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": error_msg
                        })
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    print(f"{Fore.RED}{Style.BRIGHT}[TOOL ERROR]{Style.RESET_ALL} {Fore.WHITE}{error_msg}")
                    self.llm_client.history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": error_msg
                    })              # Get the next response - this could be another tool call or a content response
            # If we're on the last iteration, set tool_choice to "none" to force a text response
            tool_choice = "none" if current_iteration >= max_iterations - 1 else "auto"
            # Using a more neutral message for continuing the conversation
            response = self.llm_client.send_prompt(None, tools=formatted_tools, tool_choice=tool_choice)
            if isinstance(response, str):
                print(f"{Fore.GREEN}{Style.BRIGHT}[AGENT RESPONSE]{Style.RESET_ALL} {Fore.WHITE}{response}")
                return response
        
        # If we've reached max iterations or got a non-string response with no content
        if hasattr(response, 'content') and response.content:
            print(f"{Fore.GREEN}{Style.BRIGHT}[AGENT RESPONSE]{Style.RESET_ALL} {Fore.WHITE}{response.content}")
            return response.content
            
        print(f"{Fore.RED}{Style.BRIGHT}[AGENT RESPONSE]{Style.RESET_ALL} {Fore.WHITE}I processed your request but reached the maximum number of tool calls without a clear response.")
        return "I processed your request but reached the maximum number of tool calls without a clear response."

    def parse_llm_response(self, llm_output: str) -> Response:
        """
        Legacy method for backward compatibility.
        """
        return Response(
            Question="",
            Thought="",
            tools_used=[],
            tool_arguments={},
            Answer=llm_output
        )

    def call_tool(self, original_question: str, tools_used: list[str]) -> ToolOutput:
        """
        Legacy method for backward compatibility.
        """
        return ToolOutput(
            OriginalQuestion=original_question,
            tools_used=tools_used,
            tool_output={}
        )