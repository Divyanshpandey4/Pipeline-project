# fetcher/config.py
import os

# read from environment; sensible defaults for local dev
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", None)
OUTPUT_DIR = os.getenv("WEATHER_OUTPUT_DIR", "./data/incoming")  # folder Spark will watch
CITIES = os.getenv("WEATHER_CITIES", "Mumbai,Delhi,Chennai").split(",")
FETCH_INTERVAL_SECONDS = int(os.getenv("FETCH_INTERVAL_SECONDS", "3600"))  # default hourly
