"""Weather refresh policy and offline recovery, without network calls."""

import json
import tempfile
import unittest
from pathlib import Path

from cortex_neo.weather import INTERVAL, MAX_AGE, RETRY, Weather


class WeatherTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.config, self.cache = root / "location.json", root / "weather.json"
        self.now, self.calls, self.failing = 100000.0, 0, False
        self.place = {
            "mode": "manual_city",
            "name": "Test city",
            "region": "Test region",
            "latitude": 20,
            "longitude": -100,
        }
        self.config.write_text(json.dumps(self.place))

    def fetch(self, place):
        self.calls += 1
        if self.failing:
            raise OSError("offline")
        return {"current": {"temperature_2m": 20}, "days": [], "timezone": "UTC"}

    def reader(self):
        return Weather(self.config, self.cache, self.fetch, lambda: self.now)

    def test_no_location_never_contacts_provider(self):
        self.config.unlink()
        reader = self.reader()
        reader.refresh()
        self.assertEqual(reader.snapshot()["status"], "unconfigured")
        self.assertEqual(self.calls, 0)

    def test_refresh_interval_and_restart_cache(self):
        reader = self.reader()
        reader.refresh()
        self.now += INTERVAL - 1
        reader.refresh()
        restarted = self.reader()
        restarted.refresh()
        self.assertEqual(self.calls, 1)
        self.now += 1
        restarted.refresh()
        self.assertEqual(self.calls, 2)

    def test_offline_preserves_data_limits_retries_and_expires(self):
        reader = self.reader()
        reader.refresh()
        original = reader.snapshot()["current"]
        self.now += INTERVAL
        self.failing = True
        reader.refresh()
        self.assertEqual(reader.snapshot()["status"], "cached")
        self.assertEqual(reader.snapshot()["current"], original)
        self.now += RETRY - 1
        reader.refresh()
        self.assertEqual(self.calls, 2)
        self.now += 1
        reader.refresh()
        self.assertEqual(self.calls, 3)
        self.now += MAX_AGE
        self.assertEqual(reader.snapshot()["status"], "expired")
        self.failing = False
        reader.refresh()
        self.assertEqual(reader.snapshot()["status"], "ok")

    def test_location_change_does_not_show_old_city_weather(self):
        reader = self.reader()
        reader.refresh()
        self.place["latitude"] = 25
        self.place["name"] = "Another city"
        self.config.write_text(json.dumps(self.place))
        self.failing = True
        reader.refresh()
        self.assertEqual(reader.snapshot()["status"], "offline")
        self.assertNotIn("current", reader.snapshot())
        self.assertEqual(reader.snapshot()["location"]["name"], "Another city")

    def test_invalid_cache_and_coordinates(self):
        self.cache.write_text("[]")
        reader = self.reader()
        reader.refresh()
        self.assertEqual(reader.snapshot()["status"], "ok")
        self.place["latitude"] = 91
        self.config.write_text(json.dumps(self.place))
        reader.refresh()
        self.assertEqual(reader.snapshot()["status"], "unconfigured")
        self.assertEqual(self.calls, 1)

    def test_nonmanual_mode_never_contacts_provider(self):
        self.place["mode"] = "automatic"
        self.config.write_text(json.dumps(self.place))
        reader = self.reader()
        reader.refresh()
        self.assertEqual(reader.snapshot()["status"], "unconfigured")
        self.assertEqual(self.calls, 0)


if __name__ == "__main__":
    unittest.main()
