"""Appearance choices preserve data, safe generation and bilingual contracts."""

import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from lua_harness import LuaHarness

from cortex_neo.fonts import FONTS, resolve_font
from cortex_neo.i18n import catalog
from cortex_neo.layout import calculate
from cortex_neo.palettes import PALETTES, ROLES
from cortex_neo.preferences import load_preferences, theme_settings, update_preferences
from cortex_neo.render import config


class AppearanceTests(unittest.TestCase):
    def test_exact_ubuntu_accents_define_every_color(self):
        self.assertEqual(
            list(PALETTES),
            [
                "blue",
                "teal",
                "green",
                "yellow",
                "orange",
                "red",
                "pink",
                "purple",
                "slate",
                "brown",
            ],
        )
        for name, values in PALETTES.items():
            self.assertEqual(set(values), set(ROLES), name)
            for color in values.values():
                self.assertRegex(color, "^[0-9A-F]{6}$")
            plan = calculate((0, 0, 1920, 1080))
            plan["theme"] = {"palette": name}
            output = config("cpu", plan["cards"]["cpu"], plan, {})
            self.assertIn(values["graph"] + " " + values["primary"], output)
            self.assertIn("default_color='" + values["text"] + "'", output)

    def test_invalid_preferences_are_atomic_and_unknown_keys_survive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "settings.json").write_text('{"custom":42,"language":"es"}')
            for choices in (
                {"language": "../../etc/passwd"},
                {"font": "${exec evil}"},
                {"detail_level": "bad"},
            ):
                before = (root / "settings.json").read_bytes()
                with self.assertRaises(ValueError):
                    update_preferences(root, **choices)
                self.assertEqual(before, (root / "settings.json").read_bytes())
            result = update_preferences(
                root, font="dejavu", detail_level="essential", palette="teal"
            )
            self.assertEqual(
                (result["custom"], result["language"], result["detail_level"]),
                (42, "es", "essential"),
            )
            self.assertEqual(load_preferences(root)["theme"]["palette"], "teal")
            self.assertEqual(theme_settings({"palette": None})["palette"], "blue")

    def test_fonts_reject_silent_substitution_and_keep_icons_separate(self):
        resolve_font.cache_clear()
        self.addCleanup(resolve_font.cache_clear)
        with patch(
            "cortex_neo.fonts.command", side_effect=["DejaVu Sans Mono", "DejaVu Sans Mono"]
        ):
            self.assertEqual(resolve_font("liberation"), "DejaVu Sans Mono")
        resolve_font.cache_clear()
        for name, family in FONTS.items():
            with patch("cortex_neo.fonts.command", return_value=family):
                plan = calculate((0, 0, 1920, 1080))
                plan["font"] = name
                text = config("cpu", plan["cards"]["cpu"], plan, {})
                self.assertIn(family + ":", text)
                self.assertIn("FontAwesome", text)
            resolve_font.cache_clear()

    def test_catalogs_have_identical_keys_and_format_fields(self):
        en, es = catalog("en"), catalog("es")
        self.assertGreater(len(en), 150)
        self.assertEqual(en.keys(), es.keys())
        for key in en:
            # Conky markup has literal braces; compare only Python format placeholders.
            def fields(text):
                return set(__import__("re").findall(r"\{(p\d+)(?:[!:][^}]*)?\}", text))

            self.assertEqual(fields(en[key]), fields(es[key]), key)
        self.assertEqual(catalog("../../invalid"), en)

    def test_essential_hides_metadata_without_hiding_main_facts(self):
        snapshot = {
            "sampled_at": time.time(),
            "os": {"name": "Test Linux", "codename": "test-codename", "kernel": "test-kernel"},
            "hardware": {
                "cpu_model": "Test CPU",
                "cpu_topology": "8 cores / 16 threads",
                "ram_model": "Test RAM",
                "ram_type": "DDR4",
                "ram_speed": "3200 MT/s",
            },
            "gpu": {"model": "Test GPU", "driver": "secret-driver"},
            "software": [
                {
                    "group": "Languages",
                    "label": "Rust",
                    "version": "1.99",
                    "detail": "private-build",
                }
            ],
        }
        for level in ("full", "essential"):
            view = LuaHarness(snapshot, ui={"detail_level": level, "translations": catalog("en")})
            self.addCleanup(view.close)
            self.assertIn("Test CPU", view.call("cpu_meta"))
            self.assertIn("Rust", view.call("software"))
            self.assertEqual("8 cores" in view.call("cpu_meta"), level == "full")
            self.assertEqual("DDR4" in view.call("ram_meta"), level == "full")
            self.assertEqual("secret-driver" in view.call("gpu_meta"), level == "full")
            self.assertEqual("private-build" in view.call("software"), level == "full")
            self.assertIn("Test Linux", view.call("system_meta"))
            self.assertEqual("test-kernel" in view.call("system_meta"), level == "full")

    def test_languages_translate_static_content_not_device_strings(self):
        snapshot = {
            "sampled_at": time.time(),
            "hardware": {"cpu_model": "Live CPU"},
            "calendar": {"month": 10, "year": 2026, "day": 25, "weeks": [[0, 0, 0, 0, 0, 24, 25]]},
            "software": [{"group": "Languages", "label": "Rust", "version": "1.99"}],
        }
        for language, month, heading in (
            ("en", "OCTOBER", "LANGUAGES"),
            ("es", "OCTUBRE", "LENGUAJES"),
        ):
            view = LuaHarness(snapshot, ui={"translations": catalog(language)})
            self.addCleanup(view.close)
            self.assertIn(month, view.call("calendar"))
            self.assertIn(heading, view.call("software"))
            self.assertIn("Live CPU", view.call("cpu_meta"))

    def test_runtime_catalogs_are_valid_utf8_data(self):
        for language in ("en", "es"):
            path = Path(__file__).resolve().parents[1] / "cortex_neo/locales" / (language + ".json")
            self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)
