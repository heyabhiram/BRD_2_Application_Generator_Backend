import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://genailab.tcs.in")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "azure_ai/genailab-maas-DeepSeek-V3-0324")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Generated apps directory under user's Downloads
    DOWNLOADS_DIR: Path = Path.home() / "Downloads" / "generated_apps"

settings = Settings()
settings.DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

