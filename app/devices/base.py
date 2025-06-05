from abc import ABC, abstractmethod
from typing import Dict

class DeviceControlInterface(ABC):
    """
    Abstract layer for controlling smart devices (simulated or physical).

    Role:
    - Apply actions to simulated or real devices
    - Track and report current device states
    """

    @abstractmethod
    def control_device(self, command: Dict[str, str]) -> str:
        """
        Input: Dict[str, str] — Device command (e.g., {"device": "tv", "location": "living room", "action": "on"})
        Output: str — Action result (e.g., "Living room TV turned on.")
        Called by: DeviceCommandAgent
        Calls: GPIO controller or simulation logic
        """
        pass

    @abstractmethod
    def get_device_states(self) -> Dict[str, str]:
        """
        Input: None
        Output: Dict[str, str] — Current device states (e.g., {"room1 ac": "off"})
        Called by: SmartHomeUIManager, DeviceCommandAgent
        Calls: internal state tracker
        """
        pass
