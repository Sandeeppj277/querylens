"""
Application configuration — loads settings from environment / .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent          # backend/
PROJECT_DIR = BASE_DIR.parent                               # Querry Converter/
load_dotenv(PROJECT_DIR / ".env")

# ── Database ─────────────────────────────────────────────
DB_PATH = BASE_DIR / "data" / "querylens.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# ── LLM (Google Gemini) ─────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# ── App ──────────────────────────────────────────────────
APP_TITLE = "QueryLens"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Natural Language → SQL → Insights"
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# ── Safety ───────────────────────────────────────────────
# Only SELECT statements are allowed for execution
ALLOWED_SQL_PREFIXES = ("select",)
MAX_RESULT_ROWS = 500
