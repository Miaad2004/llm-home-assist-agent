from .base import DeviceControlInterface
from typing import Dict, Any, Optional
from .arduino.arduino_serial_simulator import ArduinoSerialSimulator
import json
import serial

class ArduinoHardwareSimulator(DeviceControlInterface):
    """
    Simulated hardware device controller using ArduinoSerialSimulator.
    """
    def __init__(self, devices: Optional[Dict[str, Dict[str, Any]]] = None):
        self.simulator = ArduinoSerialSimulator(devices)

    def control_device(self, command: Dict[str, str]) -> str:
        """
        Input: Dict[str, str] — Device command
        Output: str — Action result
        Calls: ArduinoSerialSimulator
        """
        cmd = ArduinoSerialSimulator.build_command(
            id=command.get("id", 0),
            device_id=command.get("device_id"),
            action=command.get("action"),
            args=command.get("args", {})
        )
        response = self.simulator.serial_write(cmd)
        return response.get("msg", str(response))

    def get_device_states(self) -> Dict[str, Any]:
        """
        Input: None
        Output: Dict[str, Any] — Current device states
        Calls: Returns the current simulated device states
        """
        return self.simulator.devices

class ArduinoHardwareController(DeviceControlInterface):
    """
    Real Arduino hardware device controller using serial communication.
    Implements the protocol in protocol.md.
    """
    def __init__(self, port: str = '/dev/ttyACM0', baudrate: int = 9600, timeout: float = 1.0):
        """
        Initialize the Arduino hardware controller.
        Args:
            port: Serial port for Arduino (e.g., 'COM3' or '/dev/ttyACM0')
            baudrate: Serial baudrate
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        if serial is not None:
            try:
                self.serial = serial.Serial(port, baudrate, timeout=timeout)
            except Exception as e:
                print(f"[ArduinoHardwareController] Serial connection failed: {e}")
        else:
            print("[ArduinoHardwareController] pyserial not installed. Real hardware control will not work.")

    def control_device(self, command: Dict[str, Any]) -> str:
        """
        Send a device command to the Arduino and return the response message.
        """
        if self.serial is None:
            return "[ArduinoHardware] Serial connection not available."
        # Build protocol-compliant command
        cmd = ArduinoSerialSimulator.build_command(
            id=command.get("id", 0),
            device_id=command.get("device_id"),
            action=command.get("action"),
            args=command.get("args", {})
        )
        try:
            # Send JSON as a single line
            self.serial.write((json.dumps(cmd) + '\n').encode('utf-8'))
            self.serial.flush()
            # Read response (single line)
            response_line = self.serial.readline().decode('utf-8').strip()
            response = json.loads(response_line)
            return response.get("msg", str(response))
        except Exception as e:
            return f"[ArduinoHardware] Communication error: {e}"

    def get_device_states(self) -> Dict[str, Any]:
        """
        Query the Arduino for all device states (if supported by protocol).
        """
        # This protocol does not define a standard state query, so we return a status or could implement a custom action
        # Example: send a special action 'get_states' if supported by Arduino firmware
        if self.serial is None:
            return {"status": "[ArduinoHardware] Serial connection not available."}
        try:
            cmd = ArduinoSerialSimulator.build_command(
                id="state_query",
                device_id="system",
                action="get_states"
            )
            self.serial.write((json.dumps(cmd) + '\n').encode('utf-8'))
            self.serial.flush()
            response_line = self.serial.readline().decode('utf-8').strip()
            response = json.loads(response_line)
            return response
        except Exception as e:
            return {"status": f"[ArduinoHardware] State query error: {e}"}


