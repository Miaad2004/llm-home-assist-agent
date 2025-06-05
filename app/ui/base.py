from abc import ABC, abstractmethod
from typing import Dict

class SmartHomeUIManager(ABC):
    """
    Manages user interface logic and interactions.

    Role:
    - Collect text and voice input
    - Send commands to the agent
    - Display responses and device states
    """

    @abstractmethod
    def send_text_command(self, user_text: str) -> None:
        """
        Input: str — User command typed into the interface
        Output: None
        Called by: UI frontend event
        Calls: DeviceCommandAgent.handle_user_input(), display_response()
        """
        pass

    @abstractmethod
    def start_voice_input(self) -> None:
        """
        Input: None
        Output: None
        Called by: UI voice input button
        Calls: VoiceAssistantInterface.wait_for_command(), DeviceCommandAgent.handle_user_input(), display_response(), VoiceAssistantInterface.speak()
        """
        pass

    @abstractmethod
    def display_response(self, text: str) -> None:
        """
        Input: str — System message to show in the interface
        Output: None
        Called by: send_text_command(), start_voice_input()
        Calls: UI renderer
        """
        pass

    @abstractmethod
    def update_device_status_ui(self, device_states: Dict[str, str]) -> None:
        """
        Input: Dict[str, str] — Device states (e.g., {"kitchen lamp": "on", "tv": "off"})
        Output: None
        Called by: DeviceCommandAgent, DeviceControlInterface
        Calls: UI renderer
        """
        pass
