from abc import ABC, abstractmethod
from typing import Dict

class SmartHomeUIManager(ABC):
    """
    Manages user interface logic and interactions.
    """

    # Assigned to: Person A (UI pipeline)
    @abstractmethod
    def send_text_command(self, user_text: str) -> None:
        """
        Input: str — User command typed into the interface
        Output: None
        Calls: DeviceCommandAgent.handle_user_input(), display_response()
        """
        pass

    # Assigned to: Person A (UI pipeline)
    @abstractmethod
    def start_voice_input(self) -> None:
        """
        Input: None
        Output: None
        Calls: VoiceAssistantInterface.wait_for_command(), DeviceCommandAgent.handle_user_input(), display_response(), VoiceAssistantInterface.speak()
        """
        pass

    # Assigned to: Person B (UI pipeline)
    @abstractmethod
    def display_response(self, text: str) -> None:
        """
        Input: str — System message to show in the interface
        Output: None
        Calls: UI renderer
        """
        pass

    # Assigned to: Person B (UI pipeline)
    @abstractmethod
    def update_device_status_ui(self, device_states: Dict[str, str]) -> None:
        """
        Input: Dict[str, str] — Device states
        Output: None
        Calls: UI renderer
        """
        pass
