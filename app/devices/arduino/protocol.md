# Arduino Serial Protocol for Smart Home Assistant

## Overview

Defines the serial communication protocol between the Smart Home Assistant backend and Arduino-based devices.

## Message Format

- Commands are sent as ASCII text, one per line, terminated by `\n`.
- Responses are sent as ASCII text, one per line, terminated by `\n`.

## Supported Commands

- `SET LIGHT ON` — Turn on relay/light
- `SET LIGHT OFF` — Turn off relay/light
- `GET TEMP` — Request temperature/sensor value

## Example Session

```
> SET LIGHT ON
< OK LIGHT ON
> GET TEMP
< TEMP 512
```

## Error Handling

- Unknown commands: `ERR UNKNOWN`

## Extending

Add more commands as needed for additional devices or sensors.
