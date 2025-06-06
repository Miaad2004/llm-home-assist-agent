from .base import DeviceCommandAgent, CommandDict
from .llm_client import LLMClientInterface
from app.devices.simulator import DeviceSimulator  # or hardware import as needed
from typing import Literal, Dict, List, Any, Optional, Callable
import json
import re
from app.data.weather_api import WeatherAPI
from app.data.news_api import NewsAPI
from app.data.time_utils import TimeUtils

class DeviceCommandAgentImpl(DeviceCommandAgent):
    """
    Concrete implementation of DeviceCommandAgent using an LLM client and device control.
    """

    def __init__(self, llm_client: LLMClientInterface, device_controller=None):
        """
        Input: llm_client (LLMClientInterface), device_controller (optional)
        Output: None
        Calls: None (constructor)
        """
        self.llm_client = llm_client
        self.device_controller = device_controller or DeviceSimulator()
        self.weather_api = WeatherAPI()
        self.news_api = NewsAPI()
        self.time_utils = TimeUtils()
        
        # Add conversation history
        self.conversation_history = []
        
        # Register available functions for function calling
        self.available_functions = {
            "get_weather": self._get_weather,
            "get_news": self._get_news,
            "get_time": self._get_time,
            "control_device": self._control_device
        }
        
        # Function schemas for LLM function calling
        self.function_schemas = [
            {
                "name": "get_weather",
                "description": "Get current weather information",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_news",
                "description": "Get latest news headlines",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "count": {
                            "type": "integer",
                            "description": "Number of headlines to fetch"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_time",
                "description": "Get current time and date",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "control_device",
                "description": "Control a smart home device",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device": {
                            "type": "string",
                            "description": "Type of device (light, tv, ac, blind, etc.)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Room or area where the device is located"
                        },
                        "action": {
                            "type": "string",
                            "description": "Action to perform (on, off, up, down, set)"
                        },
                        "value": {
                            "type": "string",
                            "description": "Value for the action (temperature, channel, etc.)"
                        }
                    },
                    "required": ["device", "action"]
                }
            }
        ]

    def handle_user_input(self, user_text: str) -> str:
        """
        Input: str — Raw user input
        Output: str — System message
        Calls: self.llm_client.send_prompt(), self.parse_llm_response(), self.call_device_function()
        Action: Process user input, parse, and execute command
        """
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_text})
        
        # Check if input is a request for live data (backward compatibility)
        data_request = self._check_for_data_request(user_text)
        if data_request:
            response = self.get_live_data(data_request)
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
            
        # Build prompt with function calling capabilities
        prompt = self._build_prompt_with_functions(user_text)
        
        # Send prompt to LLM
        llm_response = self.llm_client.send_prompt_with_functions(
            prompt, 
            self.function_schemas
        )
        
        # Process response - might include function calls
        response = self._process_llm_response(llm_response)
        
        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response

    def _process_llm_response(self, llm_response: Dict) -> str:
        """Process LLM response which may include function calls"""
        # Check if function call is present
        if "function_call" in llm_response:
            function_call = llm_response["function_call"]
            function_name = function_call.get("name")
            function_args = json.loads(function_call.get("arguments", "{}"))
            
            # Execute the function if it exists
            if function_name in self.available_functions:
                function_to_call = self.available_functions[function_name]
                function_response = function_to_call(**function_args)
                
                # Add function result to conversation history
                self.conversation_history.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_response)
                })
                
                # If it's a device control function, return formatted response
                if function_name == "control_device":
                    return function_response
                    
                # For other functions, ask LLM to format the response
                return self._format_function_response(function_name, function_response)
            
        # If no function call or text response is present
        return llm_response.get("content", "I'm not sure how to help with that.")
        
    def _format_function_response(self, function_name: str, function_result: Any) -> str:
        """Format function results into human-readable responses"""
        # Build prompt for formatting the function result
        prompt = f"""
        You are a helpful smart home assistant. 
        Format the following {function_name} function result into a natural, helpful response:
        {json.dumps(function_result)}
        
        Just provide the formatted response with no additional explanations.
        """
        
        # Send to LLM for formatting
        formatted_response = self.llm_client.send_prompt(prompt)
        return formatted_response
        
    def _get_weather(self) -> Dict[str, Any]:
        """Function to get weather data"""
        weather_data = self.weather_api.get_current_weather()
        return {"weather": weather_data}
        
    def _get_news(self, count: int = 3) -> Dict[str, Any]:
        """Function to get news headlines"""
        headlines = self.news_api.get_latest_headlines(count)
        return {"headlines": headlines}
        
    def _get_time(self) -> Dict[str, Any]:
        """Function to get current time and date"""
        current_time = self.time_utils.get_current_time()
        current_date = self.time_utils.get_current_date()
        return {"time": current_time, "date": current_date}
        
    def _control_device(self, device: str, action: str, location: str = "", value: str = "") -> str:
        """Function to control a device"""
        command = {
            "device": device,
            "location": location,
            "action": action,
            "value": value
        }
        return self.call_device_function(command)

    def _build_prompt_with_functions(self, user_text: str) -> str:
        """Build a prompt that supports function calling"""
        # Creating a system message that describes the agent's capabilities
        system_message = """
You are a smart home assistant capable of controlling various devices and providing information.
You can control lights, TVs, air conditioners, blinds, and other smart home devices.
You can also provide weather information, news headlines, and tell the time.

When presented with a user request, determine if you should:
1. Call a function to control a device
2. Call a function to get information (weather, news, time)
3. Provide a direct response

Always use the most appropriate function for the task.
"""
        
        # Include conversation history for context (limited to last 10 exchanges)
        messages = [{"role": "system", "content": system_message}]
        history_to_include = self.conversation_history[-10:] if len(self.conversation_history) > 10 else self.conversation_history
        messages.extend(history_to_include)
        
        # Add current user message
        messages.append({"role": "user", "content": user_text})
        
        return messages
    
    def handle_user_input(self, user_text: str) -> str:
        """
        Input: str — Raw user input
        Output: str — System message
        Calls: self.llm_client.send_prompt(), self.parse_llm_response(), self.call_device_function()
        Action: Process user input, parse, and execute command
        """
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_text})
        
        # Check if input is a request for live data
        data_request = self._check_for_data_request(user_text)
        if data_request:
            return self.get_live_data(data_request)
            
        # Send prompt to LLM
        prompt = self._build_prompt(user_text)
        llm_response = self.llm_client.send_prompt(prompt)
        
        # Parse response into command
        command_dict = self.parse_llm_response(llm_response)
        
        # If valid command was parsed, call device function
        if command_dict:
            return self.call_device_function(command_dict)
          # Fallback response if no command was recognized
        return f"I'm not sure how to help with '{user_text}'. Could you phrase that differently?"
        
    def _check_for_data_request(self, text: str) -> Literal["weather", "news", "time", ""]:
        """Helper method to check if user is requesting weather, news, or time data"""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ["weather", "temperature", "forecast"]):
            return "weather"
        elif any(keyword in text_lower for keyword in ["news", "headlines", "events"]):
            return "news"
        elif any(keyword in text_lower for keyword in ["time", "clock", "hour"]):
            return "time"
        
        return ""

    def _build_prompt(self, user_text: str) -> str:
        """Builds a prompt for the LLM that guides it to produce structured output"""
        return f"""
You are a smart home assistant. Parse the following user request into a structured command.
The output should be in this format:
```json
{{
  "device": "[device type: light/tv/ac/blind/etc]",
  "location": "[room/area]",
  "action": "[on/off/up/down/set]",
  "value": "[any value like temperature, channel, etc if applicable]"
}}
```
If you can't determine a field, use empty string.
If the request isn't a device control command, return empty JSON: {{}}.

User request: {user_text}

JSON response:
"""

    def get_live_data(self, data_type: Literal["weather", "news", "time"]) -> str:
        """
        Input: Literal — Data type
        Output: str — Live data value
        Calls: WeatherAPI.get_current_weather(), NewsAPI.get_latest_headlines(), TimeUtils.get_current_time()
        Action: Fetch live data from APIs
        """
        if data_type == "weather":
            weather_data = self.weather_api.get_current_weather()
            return f"Current weather: {weather_data}"
        
        elif data_type == "news":
            headlines = self.news_api.get_latest_headlines(3)
            formatted_news = "\n• " + "\n• ".join(headlines)
            return f"Latest headlines:{formatted_news}"
        
        elif data_type == "time":
            current_time = self.time_utils.get_current_time()
            current_date = self.time_utils.get_current_date()
            return f"The time is {current_time} on {current_date}"
        
        return "Unknown data type requested."

    def parse_llm_response(self, llm_output: str) -> CommandDict:
        """
        Input: str — LLM output
        Output: CommandDict — Parsed command
        Calls: None (parsing logic)
        Action: Parse LLM output to command dict
        """
        # Try to extract JSON from the response
        json_match = re.search(r'```json\s*(.*?)\s*```', llm_output, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without markdown formatting
            json_match = re.search(r'({.*})', llm_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                return {}
        
        try:
            command_dict = json.loads(json_str)
            return command_dict
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from LLM output: {llm_output}")
            return {}

    def call_device_function(self, command: CommandDict) -> str:
        """
        Input: CommandDict — Structured command
        Output: str — Execution result
        Calls: self.device_controller.control_device()
        Action: Call device control interface
        """
        # Validate command has required fields
        if not command or not all(k in command for k in ["device", "action"]):
            return "Invalid command structure. Missing required fields."
        
        # Send command to device controller and get result
        result = self.device_controller.control_device(command)
        
        # Format a human-readable response
        device = command.get("device", "")
        action = command.get("action", "")
        location = command.get("location", "")
        value = command.get("value", "")
        
        response = f"{device.capitalize()} in {location} " if location else f"{device.capitalize()} "
        
        if action in ["on", "off"]:
            response += f"turned {action}"
        elif action == "set" and value:
            response += f"set to {value}"
        else:
            response += f"{action}"
            
        if value and action != "set":
            response += f" to {value}"
            
        return response

    def parse_command(self, text: str) -> dict:
        """
        Input: str — Raw user text
        Output: dict — Parsed command using LLM
        Calls: self.llm_client.send_prompt()
        """
        prompt = self._build_prompt(text)
        llm_response = self.llm_client.send_prompt(prompt)
        return self.parse_llm_response(llm_response)

    def execute_command(self, command: dict) -> str:
        """
        Input: dict — Parsed command
        Output: str — Execution result
        Calls: self.call_device_function()
        """
        return self.call_device_function(command)
