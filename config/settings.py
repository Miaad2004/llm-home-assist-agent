import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    TOGETHERAI_API_KEY = os.getenv("TOGETHERAI_API_KEY")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    GROQ_API_ENDPOINT = "https://api.groq.com/openai/v1/"

