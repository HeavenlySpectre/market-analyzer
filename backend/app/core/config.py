import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

settings = Settings()

if not settings.GEMINI_API_KEY:
    raise ValueError("FATAL ERROR: GEMINI_API_KEY tidak ditemukan di file .env")