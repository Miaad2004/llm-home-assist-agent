import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    WEATHER_API_ENDPOINT = os.getenv("WEATHER_API_ENDPOINT")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    NEWS_API_ENDPOINT = os.getenv("NEWS_API_ENDPOINT")
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_API_ENDPOINT = os.getenv("LLM_API_ENDPOINT")
    LLM_MODEL = os.getenv("LLM_MODEL")
    SYSTEM_PROMPT_PATH = os.getenv("SYSTEM_PROMPT_PATH")
    VERBOSE_LEVEL = int(os.getenv("VERBOSE_LEVEL", 1))
    USE_ARDUINO_SIMULATOR = os.getenv("USE_ARDUINO_SIMULATOR", "false")
    ARDUINO_PORT = os.getenv("ARDUINO_PORT", "COM3" if os.name == "nt" else "/dev/ttyACM0")
    ARDUINO_BAUDRATE = os.getenv("ARDUINO_BAUDRATE", "9600")
    DEVICES_CONFIG_PATH = os.getenv("DEVICES_CONFIG_PATH", os.path.join(os.path.dirname(__file__), '..', 'config', 'devices.json'))
    DOWNLOAD_FOLDER_PATH = os.getenv("DOWNLOAD_FOLDER_PATH", os.path.join(os.path.dirname(__file__), '..', 'downloads'))
    WHISPER_MODEL_PATH = os.getenv("WHISPER_MODEL_PATH", os.path.join(os.path.dirname(__file__), '..', 'app', 'voice', 'base.pt'))
    HF_TOKEN = os.getenv("HF_TOKEN")
    TTS_MODEL = os.getenv("TTS_MODEL", "XTTS")  # Default to XTTS if not set
    XTTS_PATH = os.getenv("XTTS_PATH")
    XTTS_MALE_VOICE = os.getenv("XTTS_MALE_VOICE", "Viktor Eka")  # Default voice for XTTS
    XTTS_FEMALE_VOICE = os.getenv("XTTS_FEMALE_VOICE", "Lidiya Szekeres")  # Default voice for XTTS
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))  # Default temperature for LLM
    
