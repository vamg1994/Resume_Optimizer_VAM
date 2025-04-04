from pathlib import Path
from typing import Dict, List
import os

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create necessary directories
for directory in [TEMPLATES_DIR, OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# File processing settings
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
SUPPORTED_FILE_TYPES = {
    "application/pdf": "PDF",
    "text/markdown": "Markdown",
    "text/plain": "Text",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX"
}

# Resume structure settings
REQUIRED_CV_SECTIONS = [
    'name', 'contact', 'professional_summary', 
    'work_experience', 'education', 'skills'
]

# PDF export settings
PDF_SETTINGS = {
    "font_size": {
        "header": 14,
        "section": 10,
        "body": 10
    },
    "spacing": 3.5,
    "margins": {
        "left": 15,
        "top": 15,
        "right": 15
    }
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "app.log",
            "formatter": "standard"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file", "console"]
    }
} 