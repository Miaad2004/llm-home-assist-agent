from abc import ABC, abstractmethod
from typing import Dict, Literal

CommandDict = Dict[str, str]

class DeviceCommandAgent(ABC):
    """
    Handles LLM communication, command parsing, and device function routing.

    Role: 
    - Interpret text commands from users (text or transcribed)
    - Interface with LLMs to understand intent
    - Parse structured actions and execute them via device control layer
    """

    @abstractmethod
    def handle_user_input(self, user_text: str) -> str:
        """
        Input: str — Raw text from user input or transcribed voice command
        Output: str — Final system message to return to the user (e.g., "TV turned on.")
        Called by: SmartHomeUIManager, VoiceAssistantInterface
        Calls: send_prompt(), parse_llm_response(), call_device_function()
        """
        pass

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
