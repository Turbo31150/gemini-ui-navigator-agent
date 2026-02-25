"""Configuration for Gemini UI Navigator Agent."""

import os

# Google Cloud
PROJECT_ID = os.environ.get("PROJECT_ID", "")
LOCATION = os.environ.get("LOCATION", "us-central1")
MODEL = os.environ.get("MODEL", "gemini-live-2.5-flash-native-audio")

# Server
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8080"))
DEV_MODE = os.environ.get("DEV_MODE", "true").lower() == "true"
SESSION_TIME_LIMIT = int(os.environ.get("SESSION_TIME_LIMIT", "300"))

# Browser
BROWSER_WIDTH = 1280
BROWSER_HEIGHT = 900
SCREENSHOT_QUALITY = 70
SCREENSHOT_FPS = 1  # Gemini Live API limit: 1 FPS for video
DEFAULT_URL = "https://www.google.com"

# Voice
DEFAULT_VOICE = "Puck"
