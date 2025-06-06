# Smart Home Assistant

A modular, voice-enabled smart home assistant with LLM-based command parsing, device control, and UI integration.

## Structure

- `app/`: Core logic (agent, voice, UI, devices, data)
- `tests/`: Unit/integration tests
- `scripts/`: Utility scripts
- `config/`: Settings and constants

## Setup

1. Copy `.env.example` to `.env` and fill in API keys/configs.
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the app:
   ```sh
   python scripts/run_app.py
   ```

## Cross-platform usage

### Windows

Run:

```powershell
./run_app.ps1
```

### Linux (bash)

Run:

```bash
./run_app.sh
```

### Mac (zsh)

Run:

```zsh
./run_app.zsh
```

> Ensure you have Python 3 and `venv` installed. The scripts will create a virtual environment and install dependencies automatically.

If you encounter permission errors, you may need to run:

```bash
chmod +x run_app.sh run_app.zsh
```

## Contributors

- Person A: Agent/LLM
- Person B: Voice
- Person C: UI/Devices
