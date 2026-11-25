import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Groq API
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
    LLM_MODEL = "openai/gpt-4o"  # Using Groq-supported model; swap to openai/gpt-oss-120b when available
    GROQ_MODEL = "llama-3.3-70b-versatile"  # Primary Groq model

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "smart-farming-secret-2024")
    DEBUG = os.getenv("DEBUG", "True") == "True"
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Weather API (OpenWeatherMap - free tier)
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "your_openweather_key_here")
    WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

    # RAG settings
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    TOP_K_RESULTS = 3

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
