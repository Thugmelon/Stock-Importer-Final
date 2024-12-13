"""
Configuration settings for the stock importer application.

This module contains all configuration variables used across the application.
"""
from pathlib import Path

# File paths
DATA_DIR = Path("data")
CREDENTIALS_FILE = DATA_DIR / "credentials.txt"
STOCKS_FILE = DATA_DIR / "stocks.csv"

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# Default credentials (moved to top for visibility)
DEFAULT_USERNAME = "pybro"
DEFAULT_PASSWORD = "python"

# Theme configuration
THEME = {
    "font_family": "Roboto",
    "title_size": 24,
    "normal_size": 12,
    "button_size": 14,
    "padding": 12,
    "colors": {
        "primary": "#2563eb",
        "background": "#1e293b",
        "error": "#ef4444",
        "success": "#22c55e",
        "text": "#f8fafc",
        "text_dark": "#1e293b"
    }
}

# Window settings
LOGIN_WINDOW_SIZE = "500x350"
MAIN_WINDOW_SIZE = "800x600"