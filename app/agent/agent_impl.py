from .base import DeviceCommandAgent, CommandDict
from .llm_client import LLMClientInterface

from abc import ABC, abstractmethod
from typing import Dict, Literal

import json
import ast
import pydantic
import datetime
import random

CommandDict = Dict[str, str]


class Response(pydantic.BaseModel):
    Question: str
    Thought: str
    tools_used: list[str]
    Answer: str

class ToolOutput(pydantic.BaseModel):  # Fixed typo here
    OriginalQuestion: str
    tools_used: list[str]
    tool_output: Dict[str, str]

class MyAgent(DeviceCommandAgent):
    def __init__(self, llm_client: LLMClientInterface, tools: dict):
        """
        Initialize the agent with an LLM client.
        
        :param llm_client: An instance of LLMClientInterface to communicate with the LLM.
        """
        self.llm_client = llm_client
        self.tools = tools
        
    def handle_user_input(self, user_text: str) -> str:
        """
        Input: str — Raw text from user input or transcribed voice command
        Output: str — Final system message to return to the user (e.g., "TV turned on.")
        Called by: SmartHomeUIManager, VoiceAssistantInterface
        Calls: send_prompt(), parse_llm_response(), call_device_function()
        """
        # send to llm
        llm_output = self.llm_client.send_prompt(user_text)
        res: Response = self.parse_llm_response(llm_output)
        tools_output: ToolOutput = ToolOutput(
            OriginalQuestion=user_text,
            tools_used=res.tools_used,
            tool_output={}
        )
        
        if res.tools_used:
            for tool in res.tools_used:
                if tool not in self.tools.keys():  # Fixed attribute access
                    tools_output.tool_output[tool] = "Tool does not exist"
                    continue
                
                print(f"Calling tool: {tool}")
                func = self.tools[tool]
                tool_out = func()
                tools_output.tool_output[tool] = str(tool_out)
        
        # Send tool outputs back to the LLM for final answer
        if tools_output.tools_used:
            final_prompt = f"Tool outputs: {json.dumps(tools_output.tool_output)}\nProvide a final answer."
            final_llm_output = self.llm_client.send_prompt(final_prompt)
            final_response = self.parse_llm_response(final_llm_output)
            return final_response.Answer
        
        else:
            return res.Answer

    def get_live_data(self, data_type: Literal["weather", "news", "time"]) -> str:
        """
        Input: Literal — One of: "weather", "news", or "time"
        Output: str — Current live data value (e.g., "Sunny, 24°C", "12:45 PM")
        Called by: SmartHomeUIManager
        Calls: external data APIs
        """
        if data_type == "weather":
            weather_conditions = ["Sunny", "Cloudy", "Rainy", "Windy", "Partly Cloudy"]
            temperature = random.randint(10, 35)
            return f"{random.choice(weather_conditions)}, {temperature}°C"
        
        elif data_type == "news":
            headlines = [
                "New breakthrough in renewable energy",
                "Local sports team wins championship",
                "Tech company announces latest smartphone",
                "Scientists discover new species",
                "Stock market reaches record high"
            ]
            return random.choice(headlines)
        
        elif data_type == "time":
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            return current_time
        
        return "Unknown data type requested"

    def parse_llm_response(self, llm_output: str) -> Response:
        """
        Input: str — Raw output from LLM (natural language)
        Output: Response — Parsed response from LLM
        Called by: handle_user_input()
        Calls: None
        """
        parsed_data = ast.literal_eval(llm_output)  # Only safe if you trust the source
        response = Response.parse_obj(parsed_data)
        
        return response

    def call_device_function(self, command: CommandDict) -> str:
        """
        Input: Dict[str, str] — Structured command extracted from LLM output
        Output: str — Execution result (e.g., "Room 1 AC turned off.")
        Called by: handle_user_input()
        Calls: DeviceControlInterface.control_device()
        """
        if not command or "device" not in command:
            return "No valid device command found."
        
        device = command.get("device", "").lower()
        location = command.get("location", "")
        action = command.get("action", "").lower()
        
        # Mock device control - in a real implementation, this would call actual device APIs
        devices = {
            "tv": ["on", "off", "volume_up", "volume_down", "channel_up", "channel_down"],
            "ac": ["on", "off", "temperature_up", "temperature_down"],
            "lights": ["on", "off", "dim", "brighten"],
            "thermostat": ["increase", "decrease", "set"]
        }
        
        if device not in devices:
            return f"Unknown device: {device}"
        
        if action not in devices[device]:
            return f"Invalid action '{action}' for device '{device}'"
        
        location_str = f" in {location}" if location else ""
        return f"{device.capitalize()}{location_str} {action} successfully."


