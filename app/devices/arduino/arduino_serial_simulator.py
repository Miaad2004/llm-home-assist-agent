import json
from typing import Dict, Any, Callable, Optional

class ArduinoSerialSimulator:
    """
    Simulates Arduino serial device communication using a device protocol.
    """
    def __init__(self, devices: Optional[Dict[str, Dict[str, Callable[[Dict[str, Any]], Any]]]] = None):
        """
        Initialize the simulator with a devices protocol dictionary.
        Args:
            devices: Dict mapping device_id to actions and their handlers.
        """
        if devices is None:
            # Default simulated devices and actions
            self.devices = {
                "bedroom_light": {
                    "turn_on": lambda args: (0, "Bedroom light turned on"),
                    "turn_off": lambda args: (0, "Bedroom light turned off"),
                    "set_brightness": lambda args: (
                        0, f"Brightness set to {args.get('level', '?')}%" if 0 <= args.get('level', 0) <= 100 else (1, "Brightness out of range (0-100)")
                    ) if 'level' in args else (1, "Missing required argument: level"),
                },
                "ir_led": {
                    "send_code": lambda args: (0, f"IR code {args.get('code', '?')} sent" if 'code' in args else (1, "Missing required argument: code")),
                },
            }
        else:
            self.devices = devices

    @staticmethod
    def build_command(id, device_id, action, args=None):
        """
        Build a protocol-compliant command dict for device control.
        """
        cmd = {
            "id": id,
            "device_id": device_id,
            "action": action
        }
        if args:
            cmd["args"] = args
        return cmd

    def serial_write(self, cmd: Any) -> Dict[str, Any]:
        """
        Simulate writing a command to the Arduino serial and getting a response.
        Args:
            cmd: Command dict or JSON string.
        Returns:
            dict: Response from the simulated device.
        """
        if isinstance(cmd, str):
            try:
                cmd = json.loads(cmd)
            except Exception as e:
                return {"id": None, "code": 2, "msg": f"Invalid input: {e}"}
        device_id = cmd.get("device_id")
        action = cmd.get("action")
        args = cmd.get("args", {})
        if device_id not in self.devices:
            return {"id": cmd.get("id"), "code": 1, "msg": f"Unknown device_id: {device_id}"}
        if action not in self.devices[device_id]:
            return {"id": cmd.get("id"), "code": 1, "msg": f"Unknown action: {action}"}
        try:
            result = self.devices[device_id][action](args)
            if isinstance(result, tuple) and len(result) == 2:
                code, msg = result
            else:
                code, msg = 0, str(result)
        except Exception as e:
            code, msg = 2, f"Error: {e}"
        return {"id": cmd.get("id"), "code": code, "msg": msg}
