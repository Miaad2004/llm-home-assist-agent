# Simplified Smart Home Device Control

This document explains the simplified hardware control system for the smart home assistant.

## Overview

The system uses a simple protocol to control Arduino pins directly. Each device is associated with a specific Arduino pin number, and devices can be turned on or off by setting those pins HIGH or LOW.

## Device Configuration

Devices are defined in `config/devices.json` with the following properties:

- `id`: Unique identifier for the device
- `name`: Human-readable device name
- `description`: Description of the device
- `type`: Device type (e.g., "lamp", "ac", "tv")
- `location`: Room/area where the device is located
- `pin`: Arduino pin number for controlling the device
- `status`: Current status ("on" or "off")

Example:

```json
[
  {
    "id": "bedroom_light",
    "name": "Bedroom Light",
    "description": "Ceiling LED light in the bedroom.",
    "type": "lamp",
    "location": "bedroom",
    "pin": 5,
    "status": "off"
  }
]
```

## Hardware Controller

The `ArduinoController` class in `app/devices/hardware.py` manages device states and communicates with the Arduino or uses a simulator.

It uses a simple serial protocol:

- Command format: `PIN:VALUE\n`
- Example: `5:1\n` turns pin 5 ON, `6:0\n` turns pin 6 OFF

## API Endpoints

The system provides two API endpoints for device control:

### GET /devices

Returns a list of all devices with their current status.

Example response:

```json
{
  "devices": [
    {
      "id": "bedroom_light",
      "name": "Bedroom Light",
      "description": "Ceiling LED light in the bedroom.",
      "type": "lamp",
      "location": "bedroom",
      "pin": 5,
      "status": "off"
    }
  ]
}
```

### POST /devices/control

Controls a specific device.

Request body:

```json
{
  "device_id": "bedroom_light",
  "action": "on"
}
```

Response:

```json
{
  "message": "Bedroom Light turned on",
  "status": "success"
}
```

## LLM Tools

The system provides two tools for the LLM:

### get_devices

Returns a list of all available devices with their status.

### control_device

Controls a specific device by ID.

Parameters:

- `device_id`: Device identifier
- `action`: Either "on" or "off"

## Arduino Setup

Upload the `arduino_controller.ino` sketch to your Arduino board. It listens for commands on the serial port and controls digital pins accordingly.

## Configuration

The Arduino-related settings can be configured through environment variables:

- `ARDUINO_PORT`: Serial port for Arduino (default: COM3 on Windows, /dev/ttyACM0 on Linux)
- `ARDUINO_BAUDRATE`: Serial baudrate (default: 9600)
- `USE_ARDUINO_SIMULATOR`: Set to "true" to use the simulator instead of real hardware (default: "false")

These settings can be configured in your main `.env` file.
