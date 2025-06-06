# Serial Protocol for Smart Home Devices

This document describes the protocol for communicating with smart home devices via serial using JSON objects. The device should expect to receive JSON objects that specify actions to perform on smart home devices.

## General JSON Structure

Each command sent should be a single-line JSON object with the following fields:

- `id` (string or integer): A unique identifier for this interaction. This must be unique for each request and is used to match responses.
- `device_id` (string): The unique identifier of the target device (see `devices.json`).
- `action` (string): The action to perform (must match one of the device's supported actions).
- `args` (object, optional): Arguments required for the action, if any.

### Example

```json
{
  "id": 123,
  "device_id": "your_device_id",
  "action": "your_action",
  "args": { "your_arg": "value" }
}
```

- `device_id` and `action` must match entries in your `devices.json` file.
- If the action does not require arguments, the `args` field can be omitted.

## Supported Devices and Actions

Any device defined in `devices.json` is supported. The protocol is generic: as long as the device and its actions are described in `devices.json`, the device should be able to process commands for it.

## Response Format

After processing a command, the device should return a status JSON object over serial with the following fields:

- `id` (string or integer): The unique identifier from the request, echoed back so the client can match the response to the request.
- `code` (integer): Status code (e.g., 0 for success, nonzero for errors).
- `msg` (string): Human-readable message describing the result.

### Example

```json
{ "id": 123, "code": 0, "msg": "Success" }
{ "id": 123, "code": 1, "msg": "Unknown device_id" }
{ "id": 123, "code": 2, "msg": "Missing required argument: level" }
```

The client should check the `id`, `code`, and `msg` fields to determine if the command was successful or if an error occurred, and to match responses to requests.

## Notes

- All JSON objects must be sent as a single line (no line breaks).
- The device should parse the JSON, identify the device and action, and execute the corresponding hardware command.
- If an action requires arguments, the `args` object must be present and contain the required fields.
- If an action does not require arguments, the `args` field can be omitted.

## Error Handling

- If the JSON is malformed or required fields are missing, the device should ignore the command or send an error response (implementation-specific).
- Unknown `device_id` or `action` values should be handled gracefully.

---

This protocol ensures a consistent and extensible way to control smart home devices via serial communication using JSON objects.
