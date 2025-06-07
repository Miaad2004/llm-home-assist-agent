from .base import DeviceControlInterface
from typing import Dict, Any, Optional, List
import json
import os
import serial
import signal
import atexit
import threading
import time
from dotenv import load_dotenv
from config.settings import Settings
from colorama import Fore, Style, init

init(autoreset=True)

load_dotenv()

# Global registry to track all ArduinoController instances for cleanup
_arduino_instances = []
_cleanup_lock = threading.Lock()

def _global_cleanup():
    """Global cleanup function called on exit or signal"""
    with _cleanup_lock:
        for instance in _arduino_instances:
            try:
                instance._cleanup_serial()
            except Exception as e:
                print(f"{Fore.RED}[Cleanup] Error cleaning up Arduino instance: {e}{Style.RESET_ALL}")

def _signal_handler(signum, frame):
    """Signal handler for SIGINT (Ctrl+C) and SIGTERM"""
    print(f"\n{Fore.YELLOW}[Signal] Received signal {signum}, cleaning up...{Style.RESET_ALL}")
    _global_cleanup()
    exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

# Register exit handler
atexit.register(_global_cleanup)

class DeviceConfigBase:
    def __init__(self, config_path: Optional[str] = None):
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'devices.json')
        self.config_path = config_path
        self.devices = self._load_devices(self.config_path)

    def _load_devices(self, config_path: str) -> List[Dict[str, Any]]:
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"{Fore.RED}[DeviceConfigBase] Error loading config: {e}{Style.RESET_ALL}")
            return []

    def _save_devices(self) -> bool:
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.devices, f, indent=2)
            return True
        except Exception as e:
            print(f"{Fore.RED}[DeviceConfigBase] Error saving config: {e}{Style.RESET_ALL}")
            return False

    def _find_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        for d in self.devices:
            if d["id"] == device_id:
                return d
        return None

    def _action_to_pin_value(self, action: str) -> Optional[int]:
        return 1 if action == "on" else 0 if action == "off" else None

    def _update_device_status(self, device: Dict[str, Any], action: str):
        device["status"] = action
        self._save_devices()

class ArduinoSimulator(DeviceControlInterface, DeviceConfigBase):
    def __init__(self, config_path: Optional[str] = None):
        DeviceConfigBase.__init__(self, config_path)
        self.pins = {}
        print(f"{Fore.CYAN}[ArduinoSimulator] Init{Style.RESET_ALL}")

    def _set_pin_state(self, pin: int, value: int) -> bool:
        if not isinstance(pin, int) or pin < 0 or value not in [0, 1]:
            print(f"{Fore.RED}[ArduinoSimulator] Invalid pin or value{Style.RESET_ALL}")
            return False

        self.pins[pin] = value
        print(f"{Fore.GREEN}[ArduinoSimulator] Pin {pin}={value}{Style.RESET_ALL}")
        return True

    def get_pin(self, pin: int) -> int:
        return self.pins.get(pin, 0)

    def control_device(self, command: Dict[str, Any]) -> str:
        device_id = command.get("device_id")
        action = command.get("action", "").lower()

        if not device_id:
            return "Error: device_id required"

        if action not in ["on", "off"]:
            return "Error: action must be 'on' or 'off'"

        device = self._find_device(device_id)
        if not device:
            return f"Error: Device '{device_id}' not found"

        pin = device.get("pin")
        if pin is None:
            return f"Error: No pin for '{device_id}'"

        pin_value = self._action_to_pin_value(action)
        if pin_value is None:
            return "Error: Invalid action"

        if self._set_pin_state(pin, pin_value):
            self._update_device_status(device, action)
            return f"{device['name']} turned {action}"

        return f"Error controlling {device['name']}"

    def get_device_states(self) -> Dict[str, Any]:
        for device in self.devices:
            pin = device.get("pin")
            if pin is not None:
                device["status"] = "on" if self.get_pin(pin) == 1 else "off"
        return {device["id"]: device for device in self.devices}

class ArduinoController(DeviceControlInterface, DeviceConfigBase):
    def __init__(self, config_path: Optional[str] = None):
        DeviceConfigBase.__init__(self, config_path)
        use_sim = getattr(Settings, "USE_ARDUINO_SIMULATOR", "false").lower() == "true"
        self.serial = None
        self.simulator = None
        self._is_closing = False
        
        # Register this instance for cleanup
        with _cleanup_lock:
            _arduino_instances.append(self)
        
        if use_sim:
            print(f"{Fore.YELLOW}[ArduinoController] Using simulator{Style.RESET_ALL}")
            self.simulator = ArduinoSimulator(config_path)
        else:
            try:
                port = getattr(Settings, "ARDUINO_PORT", "COM3" if os.name == "nt" else "/dev/ttyACM0")
                baud = int(getattr(Settings, "ARDUINO_BAUDRATE", "9600"))
                self.serial = serial.Serial(port, baud, timeout=1.0)
                
                # Wait for Arduino to initialize and send "Arduino Ready"
                start_time = time.time()
                ready = False
                print(f"{Fore.CYAN}[ArduinoController] Waiting for Arduino Ready...{Style.RESET_ALL}")
                while time.time() - start_time < 10:  # wait up to 10 seconds
                    line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"{Fore.MAGENTA}[ArduinoController] Arduino boot: '{line}'{Style.RESET_ALL}")
                    if "Arduino Ready" in line:
                        ready = True
                        break
                if not ready:
                    print(f"{Fore.YELLOW}[ArduinoController] Did not receive 'Arduino Ready', continuing anyway...{Style.RESET_ALL}")
                # Send test command
                self.serial.write(f"10:1\n".encode('utf-8'))
                print(f"{Fore.CYAN}[ArduinoController] Connected to {port} at {baud}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[ArduinoController] Serial failed: {e}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[ArduinoController] Fallback to simulator{Style.RESET_ALL}")
                self.simulator = ArduinoSimulator(config_path)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""
        self._cleanup_serial()

    def _cleanup_serial(self):
        """Clean up serial connection safely"""
        if self._is_closing:
            return
            
        self._is_closing = True
        
        if self.serial and self.serial.is_open:
            try:
                print(f"{Fore.YELLOW}[ArduinoController] Closing serial connection...{Style.RESET_ALL}")
                self.serial.close()
                print(f"{Fore.GREEN}[ArduinoController] Serial connection closed{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[ArduinoController] Error closing serial: {e}{Style.RESET_ALL}")
            finally:
                self.serial = None

    def __del__(self):
        """Destructor - ensure cleanup happens"""
        try:
            self._cleanup_serial()
        except:
            pass  # Ignore errors in destructor

    def control_device(self, command: Dict[str, Any]) -> str:
        device_id = command.get("device_id")
        action = command.get("action", "").lower()

        if not device_id:
            return "Error: device_id required"

        if action not in ["on", "off"]:
            return "Error: action must be 'on' or 'off'"

        device = self._find_device(device_id)
        if not device:
            return f"Error: Device '{device_id}' not found"

        pin = device.get("pin")
        if pin is None:
            return f"Error: No pin for '{device_id}'" 
               
        pin_value = self._action_to_pin_value(action)
        if pin_value is None:
            return "Error: Invalid action"

        if self._set_pin_state(pin, pin_value):
            self._update_device_status(device, action)
            return f"{device['name']} turned {action}"

        return f"Error controlling {device['name']}"

    def _set_pin_state(self, pin: int, value: int) -> bool:
        if self.simulator:
            return self.simulator._set_pin_state(pin, value)

        elif self.serial and not self._is_closing:
            try:
                # Check if serial connection is still open
                if not self.serial.is_open:
                    print(f"{Fore.RED}[ArduinoController] Serial connection is closed{Style.RESET_ALL}")
                    return False
                
                command = f"{pin}:{value}\n".encode('utf-8')
                self.serial.write(command)
                self.serial.flush()
                
                # Wait for Arduino to process and send "OK"
                response = self.serial.readline().decode('utf-8', errors='ignore').strip()
                print(f"{Fore.MAGENTA}[ArduinoController] Arduino response: '{response}'{Style.RESET_ALL}")  # <-- Added print
                return response == "OK"
            
            except serial.SerialException as e:
                print(f"{Fore.RED}[ArduinoController] Serial communication error: {e}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[ArduinoController] Attempting to close connection...{Style.RESET_ALL}")
                self._cleanup_serial()
                return False
            
            except Exception as e:
                print(f"{Fore.RED}[ArduinoController] Unexpected serial error: {e}{Style.RESET_ALL}")
                self._cleanup_serial()
                return False

        print(f"{Fore.RED}[ArduinoController] No way to control pin {pin}{Style.RESET_ALL}")
        return False

    def get_device_states(self) -> Dict[str, Any]:
        if self.simulator:
            return self.simulator.get_device_states()
        return {device["id"]: device for device in self.devices}


