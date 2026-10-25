"""Infrequent forecasts for a MANUALLY configured city.

The city must be edited manually in the user's cortex-neo/location.json.
Never discover it via GeoIP, GPS, GeoClue, nearby Wi-Fi or network identifiers.
Only the public city coordinates supplied in that file reach the weather API.
An absent/invalid manual configuration stays unconfigured; it has no fallback.
The weather worker is isolated from the live hardware sampler.
"""

import json
import math
import threading
import time
from datetime import date, datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from .io import atomic
from .paths import CACHE, CONFIG

INTERVAL = 15 * 60
RETRY = 5 * 60
MAX_AGE = 6 * 60 * 60


def location(path):
    try:
        value = json.loads(path.read_text())
        if not isinstance(value, dict) or value.get("mode") != "manual_city":
            return None
        lat, lon = float(value["latitude"]), float(value["longitude"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return None
        if not isinstance(value.get("name"), str) or not value["name"].strip():
            return None
        return {
            "name": value["name"].strip(),
            "region": value.get("region", "").strip()
            if isinstance(value.get("region"), str)
            else "",
            "latitude": lat,
            "longitude": lon,
        }
    except (OSError, ValueError, TypeError, KeyError):
        return None


def key(place):
    return [place["name"], place["region"], place["latitude"], place["longitude"]]


def fetch_forecast(place):
    params = {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,is_day,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset",
        "timezone": "auto",
        "forecast_days": 7,
        "wind_speed_unit": "kmh",
    }
    request = Request(
        "https://api.open-meteo.com/v1/forecast?" + urlencode(params),
        headers={"User-Agent": "CortexNeo/1.0 (personal desktop)", "Accept": "application/json"},
    )
    with urlopen(request, timeout=8) as response:
        value = json.load(response)
    current, daily = value["current"], value["daily"]
    temperature = float(current["temperature_2m"])
    if not math.isfinite(temperature):
        raise ValueError("Missing current temperature")
    days = []
    for index, day in enumerate(daily["time"]):
        date.fromisoformat(day)
        entry = {"date": day}
        for name in (
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "sunrise",
            "sunset",
        ):
            entry[name] = daily.get(name, [None] * len(daily["time"]))[index]
        days.append(entry)
    if not days:
        raise ValueError("Missing daily forecast")
    return {
        "current": current,
        "days": days,
        "timezone": value["timezone"],
        "attribution": "Open-Meteo / CC BY 4.0",
    }


class Weather:
    def __init__(self, config=None, cache=None, fetcher=fetch_forecast, clock=time.time):
        self.config = config or CONFIG / "location.json"
        self.cache = cache or CACHE / "weather.json"
        self.fetcher, self.clock = fetcher, clock
        self.place, self.value, self.error = None, {}, False
        self.next_request = 0
        try:
            self.value = json.loads(self.cache.read_text())
            if (
                not isinstance(self.value, dict)
                or not isinstance(self.value.get("fetched_at"), (int, float))
                or not math.isfinite(self.value["fetched_at"])
                or not 0 <= self.value["fetched_at"] <= self.clock() + 300
                or not isinstance(self.value.get("current"), dict)
                or not isinstance(self.value.get("days"), list)
            ):
                self.value = {}
        except (OSError, ValueError):
            pass

    def refresh(self):
        place = location(self.config)
        if place != self.place:
            self.place, self.next_request, self.error = place, 0, False
        if not place:
            return
        now = self.clock()
        matching = self.value.get("location_key") == key(place)
        if matching and not self.error and now - self.value.get("fetched_at", 0) < INTERVAL:
            return
        if now < self.next_request:
            return
        try:
            result = self.fetcher(place)
            value = {**result, "location": place, "location_key": key(place), "fetched_at": now}
            self.cache.parent.mkdir(parents=True, exist_ok=True)
            atomic(self.cache, json.dumps(value, ensure_ascii=False))
            self.value, self.error, self.next_request = value, False, now + INTERVAL
        except (OSError, ValueError, KeyError, TypeError, IndexError):
            self.error, self.next_request = True, now + RETRY

    def snapshot(self):
        place, value = self.place, self.value
        if not place:
            return {"status": "unconfigured"}
        if value.get("location_key") != key(place):
            return {"status": "offline" if self.error else "loading", "location": place}
        age = max(0, self.clock() - value.get("fetched_at", 0))
        status = (
            "expired" if age > MAX_AGE else ("cached" if self.error or age > INTERVAL * 2 else "ok")
        )
        try:
            zone = ZoneInfo(value.get("timezone", "UTC"))
        except (KeyError, TypeError, ValueError):
            zone = ZoneInfo("UTC")
        return {
            **value,
            "status": status,
            "age_seconds": age,
            "local_date": datetime.fromtimestamp(self.clock(), zone).date().isoformat(),
            "updated_time": datetime.fromtimestamp(value["fetched_at"], zone).strftime("%H:%M"),
        }

    def start(self):
        def worker():
            while True:
                self.refresh()
                time.sleep(30)

        threading.Thread(target=worker, name="weather", daemon=True).start()
