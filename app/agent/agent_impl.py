from .base import DeviceCommandAgent, CommandDict
from .llm_client import LLMClientInterface

from abc import ABC, abstractmethod
from typing import Dict, Literal

CommandDict = Dict[str, str]

class MyAgent(DeviceCommandAgent):
    def __init__(self, llm_client: LLMClientInterface):
        """
        Initialize the agent with an LLM client.
        
        :param llm_client: An instance of LLMClientInterface to communicate with the LLM.
        """
        self.llm_client = llm_client
        
    def handle_user_input(self, user_text: str) -> str:
        """
        Input: str — Raw text from user input or transcribed voice command
        Output: str — Final system message to return to the user (e.g., "TV turned on.")
        Called by: SmartHomeUIManager, VoiceAssistantInterface
        Calls: send_prompt(), parse_llm_response(), call_device_function()
        """
        # send to llm
        llm_output = self.llm_client.send_prompt(user_text)

    @abstractmethod
    def get_live_data(self, data_type: Literal["weather", "news", "time"]) -> str:
        """
        Input: Literal — One of: "weather", "news", or "time"
        Output: str — Current live data value (e.g., "Sunny, 24°C", "12:45 PM")
        Called by: SmartHomeUIManager
        Calls: external data APIs
        """
        pass

    @abstractmethod
    def parse_llm_response(self, llm_output: str) -> CommandDict:
        """
        Input: str — Raw output from LLM (natural language)
        Output: Dict[str, str] — Parsed command (e.g., {"device": "ac", "location": "room1", "action": "off"})
        Called by: handle_user_input()
        Calls: None
        """
        pass

    @abstractmethod
    def call_device_function(self, command: CommandDict) -> str:
        """
        Input: Dict[str, str] — Structured command extracted from LLM output
        Output: str — Execution result (e.g., "Room 1 AC turned off.")
        Called by: handle_user_input()
        Calls: DeviceControlInterface.control_device()
        """
        pass


