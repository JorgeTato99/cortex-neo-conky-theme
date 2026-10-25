"""Persistent presentation choices are data, never executable theme fragments."""

import json
import tempfile
import unittest
from pathlib import Path

from cortex_neo.layout import calculate
from cortex_neo.preferences import load_preferences, theme_settings, update_preferences
from cortex_neo.render import config


class PreferencesTests(unittest.TestCase):
    def test_palette_opacity_and_selection_reach_real_generated_config(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "settings.json").write_text('{"custom":"keep"}')
            update_preferences(
                root, palette="contrast", opacity=1, hidden=["calendar"], anchor="left"
            )
            settings = load_preferences(root)
            self.assertEqual(json.loads((root / "settings.json").read_text())["custom"], "keep")
            plan = calculate(
                (40, 20, 1400, 900), hidden=settings["hidden_cards"], anchor=settings["anchor"]
            )
            plan["theme"] = settings["theme"]
            output = config("cpu", plan["cards"]["cpu"], plan, {})
            self.assertNotIn("calendar", plan["cards"])
            self.assertAlmostEqual(plan["x"], 40 + plan["margin"])
            self.assertIn("own_window_argb_value=255", output)
            self.assertIn("default_color='FFFFFF'", output)

    def test_invalid_untrusted_theme_uses_safe_defaults(self):
        theme = theme_settings(
            {"palette": "unknown", "opacity": float("nan"), "colors": {"primary": "'${exec evil}"}}
        )
        self.assertEqual(theme["colors"]["primary"], "55AEFF")
        self.assertAlmostEqual(theme["opacity"], 190 / 255)
        self.assertEqual(theme_settings({"opacity": 0})["opacity"], 0)
        self.assertEqual(theme_settings({"opacity": 1})["opacity"], 1)

    def test_invalid_write_preserves_settings_and_system_card_cannot_disappear(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "theme.json").write_text('{"palette":"amber"}')
            previous = (root / "theme.json").read_bytes()
            with self.assertRaises(ValueError):
                update_preferences(root, opacity=2)
            self.assertEqual((root / "theme.json").read_bytes(), previous)
            update_preferences(root, hidden=["system", "cpu", "calendar", "invalid"])
            plan = calculate((0, 0, 1000, 800), hidden=load_preferences(root)["hidden_cards"])
            self.assertIn("system", plan["cards"])
            self.assertNotIn("cpu", plan["cards"])
            self.assertEqual(load_preferences(root)["theme"]["palette"], "amber")
