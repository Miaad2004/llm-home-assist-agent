from .base import DeviceCommandAgent, Response, ToolOutput
from .llm_client import LLMClientInterface

from config.settings import Settings
import json
import ast


class MyAgent(DeviceCommandAgent):
    def __init__(self, llm_client: LLMClientInterface, tools: dict, base_sys_prompt_path: str = "", device_control=None):
        """
        Initializes the agent with an LLM client, tools, and device controller.
        """
        self.tools = tools
        self.llm_client = llm_client
        self.device_control = device_control

        # Hook up device controller to generic_tools
        if device_control is not None:
            try:
                import app.tools.generic_tools as generic_tools
                generic_tools.device_controller = device_control
                
            except ImportError as e:
                print(f"[ERROR] Could not import generic_tools to set device_controller: {e}")
        
        # Set a simpler system prompt - we don't need the complex tool instructions anymore
        system_prompt = "You are a helpful smart home assistant. You can control devices, check the weather, get news, and more."
        # if base_sys_prompt_path:
        #     try:
        #         with open(base_sys_prompt_path, "r") as f:
        #             custom_prompt = f.read()
        #         if custom_prompt:
        #             system_prompt = custom_prompt
        #     except Exception as e:
        #         print(f"Could not load system prompt: {e}")
        
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
        """
        # Format tools for the API
        formatted_tools = self._format_tools_for_api()
        
        # Send the initial prompt with tool definitions
        response = self.llm_client.send_prompt(user_text, tools=formatted_tools)
        
        # If response is a string, return it directly (no tool calls)
        if isinstance(response, str):
            return response
        
        # Check if the model wants to call tools
        if hasattr(response, 'tool_calls') and response.tool_calls:
            # Process each tool call
            for tool_call in response.tool_calls:
                tool_name = tool_call.function.name
                
                try:
                    # Parse the arguments
                    args = json.loads(tool_call.function.arguments)
                    print(f"\n[TOOL CALL] {tool_name} called with parameters:")
                    print(json.dumps(args, indent=2))
                    
                    # Execute the tool
                    if tool_name in self.tools:
                        tool_function = self.tools[tool_name]["function"]
                        result = tool_function(**args)
                        print(f"[TOOL RESPONSE] {tool_name} returned:")
                        print(json.dumps(result, indent=2) if not isinstance(result, str) else result)
                        # Add the tool result to the conversation
                        self.llm_client.history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": str(result)
                        })
                    else:
                        error_msg = f"Error: Tool '{tool_name}' not found"
                        print(f"[TOOL ERROR] {error_msg}")
                        self.llm_client.history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": error_msg
                        })
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    print(f"[TOOL ERROR] {error_msg}")
                    self.llm_client.history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": error_msg
                    })
            
            # Get the final response after tool execution
            final_response = self.llm_client.send_prompt("", tools=formatted_tools)
            if isinstance(final_response, str):
                return final_response
            elif hasattr(final_response, 'content') and final_response.content:
                return final_response.content
            else:
                return "I processed your request but couldn't generate a proper response."
        
        # If there were no tool calls but we got a non-string response
        if hasattr(response, 'content'):
            return response.content
        
        return "I couldn't process your request properly."

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