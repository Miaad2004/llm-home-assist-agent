# Arduino Integration for Smart Home Assistant

This folder contains code and documentation for integrating Arduino-based devices with the Smart Home Assistant system.

## Files

- `SmartDevice.ino`: Main Arduino sketch for device control and communication.
- `helpers.h`: (Optional) Shared definitions and helper functions for the sketch.
- `protocol.md`: Protocol specification for serial or other communication between the Arduino and the main system.

## Setup

1. Flash `SmartDevice.ino` to your Arduino board using the Arduino IDE.
2. Connect the Arduino to your server (e.g., Raspberry Pi or PC) via USB.
3. Ensure the Python backend can communicate with the Arduino over serial (e.g., using `pyserial`).
4. Follow the protocol in `protocol.md` for message formatting and device commands.

## Requirements

- Arduino board (Uno, Nano, etc.)
- Arduino IDE
- USB cable
- (Optional) Sensors/relays for your smart devices

## Example Serial Command

```
SET LIGHT ON
GET TEMP
```

See `protocol.md` for full details.
