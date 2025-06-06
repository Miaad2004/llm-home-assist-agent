# Smart Home Assistant

A modular, voice-enabled smart home assistant with LLM-based command parsing, device control, and UI integration.

## Structure

- `app/`: Core logic (agent, voice, UI, devices, data)
- `tests/`: Unit/integration tests
- `scripts/`: Utility scripts
- `config/`: Settings and constants

## Setup

1. Copy `example.env` to `.env` and fill in your API keys/configs.
   - You'll need at least one of: OpenAI API key, Groq API key, or TogetherAI API key
   - Optional: Add weather and news API keys for live data
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the app:
   ```sh
   python scripts/run_app_new.py
   ```

## Usage

The Smart Home Assistant can:

1. **Control smart home devices**:

   - Turn on/off lights, AC, TV, etc.
   - Set temperatures, channels, volumes
   - Control blinds up/down

2. **Provide live information**:
   - Weather updates
   - Latest news headlines
   - Current time and date

### Example Commands

- "Turn on the living room lights"
- "Set the bedroom AC to 22 degrees"
- "What's the weather like?"
- "Tell me the latest news"
- "What time is it?"
- "Turn on the TV in the living room"
- "Close the blinds in the bedroom"
  ```

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
