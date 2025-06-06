from .base import DeviceControlInterface
from typing import Dict, Any

class DeviceSimulator(DeviceControlInterface):
    """
    Simulated device controller for testing and development.
    """
    def __init__(self):
        """Initialize device simulator with default device states"""
        self.device_states = {
            "living_room_light": {"status": "off", "brightness": "50"},
            "bedroom_light": {"status": "off", "brightness": "30"},
            "kitchen_light": {"status": "off", "brightness": "70"},
            "ac": {"status": "off", "temperature": "22", "mode": "cool"},
            "tv": {"status": "off", "channel": "5", "volume": "20"},
            "blinds": {"status": "closed", "position": "0"},
            "speaker": {"status": "off", "volume": "50"},
            "thermostat": {"status": "off", "temperature": "21"}
        }
        self.locations = {
            "living room": ["living_room_light", "tv", "ac", "blinds", "speaker"],
            "bedroom": ["bedroom_light", "ac", "blinds"],
            "kitchen": ["kitchen_light", "speaker"]
        }
    
    def control_device(self, command: Dict[str, str]) -> str:
        """
        Input: Dict[str, str] — Device command
        Output: str — Action result
        Calls: Simulated device logic
        """
        device_type = command.get("device", "").lower()
        location = command.get("location", "").lower()
        action = command.get("action", "").lower()
        value = command.get("value", "")
        
        # Find the specific device based on type and location
        device_id = self._get_device_id(device_type, location)
        
        if not device_id:
            return f"Device '{device_type}' in '{location}' not found."
        
        # Update device state based on action
        if action in ["on", "off"]:
            self.device_states[device_id]["status"] = action
            return f"{device_type.capitalize()} in {location} turned {action}."
        
        elif action == "set":
            # Determine which property to set based on device type
            if device_type == "ac" or device_type == "thermostat":
                self.device_states[device_id]["temperature"] = value
                return f"{device_type.capitalize()} in {location} set to {value}°C."
            
            elif device_type == "tv":
                if "channel" in value.lower():
                    channel = ''.join(filter(str.isdigit, value))
                    self.device_states[device_id]["channel"] = channel
                    return f"TV in {location} set to channel {channel}."
                elif "volume" in value.lower():
                    volume = ''.join(filter(str.isdigit, value))
                    self.device_states[device_id]["volume"] = volume
                    return f"TV in {location} volume set to {volume}."
            
            elif device_type == "light":
                if "brightness" in value.lower():
                    brightness = ''.join(filter(str.isdigit, value))
                    self.device_states[device_id]["brightness"] = brightness
                    return f"Light in {location} brightness set to {brightness}%."
            
            elif device_type == "blinds":
                if "open" in value.lower():
                    self.device_states[device_id]["status"] = "open"
                    self.device_states[device_id]["position"] = "100"
                    return f"Blinds in {location} opened."
                elif "close" in value.lower():
                    self.device_states[device_id]["status"] = "closed"
                    self.device_states[device_id]["position"] = "0"
                    return f"Blinds in {location} closed."
        
        elif action == "up":
            if device_type == "blinds":
                self.device_states[device_id]["status"] = "open"
                self.device_states[device_id]["position"] = "100"
                return f"Blinds in {location} opened up."
            elif device_type == "volume" or device_type == "tv" and "volume" in value.lower():
                current_vol = int(self.device_states[device_id]["volume"])
                new_vol = min(current_vol + 10, 100)
                self.device_states[device_id]["volume"] = str(new_vol)
                return f"Volume in {location} turned up to {new_vol}%."
        
        elif action == "down":
            if device_type == "blinds":
                self.device_states[device_id]["status"] = "closed"
                self.device_states[device_id]["position"] = "0"
                return f"Blinds in {location} closed down."
            elif device_type == "volume" or device_type == "tv" and "volume" in value.lower():
                current_vol = int(self.device_states[device_id]["volume"])
                new_vol = max(current_vol - 10, 0)
                self.device_states[device_id]["volume"] = str(new_vol)
                return f"Volume in {location} turned down to {new_vol}%."
        
        # Default response if no specific action was handled
        return f"Action '{action}' for {device_type} in {location} executed."

    def _get_device_id(self, device_type: str, location: str) -> str:
        """Helper method to find a specific device id based on type and location"""
        if not location:
            # If no location is specified, return the first matching device by type
            for device_id in self.device_states:
                if device_type in device_id:
                    return device_id
            return None
            
        if location in self.locations:
            for device_id in self.locations[location]:
                if device_type in device_id:
                    return device_id
                    
        # Fallback to generic device type matching if specific location device not found
        for device_id in self.device_states:
            if device_type in device_id:
                return device_id
                
        return None

    def get_device_states(self) -> Dict[str, Any]:
        """
        Input: None
        Output: Dict[str, Dict[str, str]] — Current device states
        Calls: Simulated state query
        """
        return self.device_states
