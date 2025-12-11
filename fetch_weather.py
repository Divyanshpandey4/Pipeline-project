# fetcher/fetch_weather.py
import os
import time
import json
import uuid
import logging
from datetime import datetime, timezone
import requests
from config import OPENWEATHER_API_KEY, OUTPUT_DIR, CITIES, FETCH_INTERVAL_SECONDS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if OPENWEATHER_API_KEY is None:
    raise RuntimeError("OPENWEATHER_API_KEY env var is required. Set it before running.")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logging.exception("Failed fetching weather for %s: %s", city, e)
        return None

def write_event(event_json, outdir=OUTPUT_DIR):
    # write NDJSON file with a unique name so Spark picks it up atomically
    filename = f"{uuid.uuid4().hex}.json"
    path = os.path.join(outdir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(event_json))
    logging.info("Wrote event file %s", path)

def normalize_api_response(raw):
    # pick safe fields and convert times to ISO with UTC tz
    try:
        out = {
            "city": raw.get("name"),
            "temperature": raw.get("main", {}).get("temp"),
            "humidity": raw.get("main", {}).get("humidity"),
            "weather": raw.get("weather", [{}])[0].get("description"),
            # original event time from API (seconds since epoch)
            "event_time_utc": datetime.fromtimestamp(raw.get("dt", int(time.time())), tz=timezone.utc).isoformat(),
            "raw": raw
        }
        return out
    except Exception:
        logging.exception("Failed to normalize response")
        return None

def main_loop():
    while True:
        for city in CITIES:
            raw = fetch_weather(city.strip())
            if raw:
                normalized = normalize_api_response(raw)
                if normalized:
                    write_event(normalized)
        logging.info("Sleeping %s seconds", FETCH_INTERVAL_SECONDS)
        time.sleep(FETCH_INTERVAL_SECONDS)

if __name__ == "__main__":
    main_loop()
