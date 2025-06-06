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