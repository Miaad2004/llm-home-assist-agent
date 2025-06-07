# API Server Usage Guide

The `start_api.ps1` script has been enhanced to support various parameters and automatic virtual environment management.

## Basic Usage

```powershell
# Start with default settings (port 8000, with reload)
.\start_api.ps1

# Start on a different port
.\start_api.ps1 -Port 3000

# Start on a specific host and port
.\start_api.ps1 -Host "127.0.0.1" -Port 5000

# Start without auto-reload (for production)
.\start_api.ps1 -NoReload

# Force reinstall requirements
.\start_api.ps1 -ForceInstall

# Change log level
.\start_api.ps1 -LogLevel "debug"

# Combine multiple parameters
.\start_api.ps1 -Port 8080 -Host "0.0.0.0" -LogLevel "warning" -ForceInstall
```

## Parameters

| Parameter       | Type   | Default   | Description                                       |
| --------------- | ------ | --------- | ------------------------------------------------- |
| `-Port`         | int    | 8000      | Port number for the API server                    |
| `-Host`         | string | "0.0.0.0" | Host address to bind to                           |
| `-NoReload`     | switch | false     | Disable auto-reload (useful for production)       |
| `-ForceInstall` | switch | false     | Force reinstall all requirements                  |
| `-LogLevel`     | string | "info"    | Log level (debug, info, warning, error, critical) |

## Features

### Automatic Virtual Environment Management

- Creates virtual environment if it doesn't exist
- Installs all requirements automatically
- Uses the virtual environment's Python executable
- Sets up PYTHONPATH correctly

### Error Handling

- Checks for successful virtual environment creation
- Validates requirements installation
- Provides clear error messages with appropriate exit codes

### Flexible Configuration

- Customizable host and port
- Optional auto-reload for development
- Configurable log levels
- Force reinstall option for troubleshooting

## Examples

### Development Mode

```powershell
# Standard development setup with auto-reload
.\start_api.ps1

# Development on custom port with debug logging
.\start_api.ps1 -Port 3000 -LogLevel "debug"
```

### Production Mode

```powershell
# Production setup without auto-reload
.\start_api.ps1 -NoReload -LogLevel "warning"

# Production on specific port and host
.\start_api.ps1 -Host "192.168.1.100" -Port 80 -NoReload
```

### Troubleshooting

```powershell
# Reinstall all packages and start
.\start_api.ps1 -ForceInstall

# Debug mode with package reinstall
.\start_api.ps1 -ForceInstall -LogLevel "debug"
```

## Access Points

Once started, the API will be available at:

- **Main API**: `http://{Host}:{Port}/`
- **Interactive Documentation**: `http://{Host}:{Port}/docs`
- **OpenAPI Schema**: `http://{Host}:{Port}/openapi.json`

## Notes

- The script automatically creates and manages the virtual environment
- All dependencies from `requirements.txt` are installed automatically
- The script sets the correct `PYTHONPATH` for module imports
- Use `Ctrl+C` to stop the server gracefully
