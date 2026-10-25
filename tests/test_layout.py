"""Work-area bounds, proportional scaling and absent-card reflow."""

import unittest

from cortex_neo.layout import calculate


class LayoutTests(unittest.TestCase):
    def test_resolution_matrix_and_equal_rows(self):
        for area in [
            (67, 32, 1469, 832),
            (67, 32, 1299, 736),
            (67, 32, 1213, 688),
            (67, 32, 2493, 1408),
            (67, 32, 3773, 2128),
            (67, 32, 3373, 1408),
            (0, 32, 1080, 1888),
        ]:
            with self.subTest(area=area):
                plan = calculate(area, calendar_weeks=6)
                self.assertLessEqual(plan["x"] + plan["width"], area[0] + area[2] + 0.01)
                self.assertLessEqual(plan["y"] + plan["height"], area[1] + area[3] + 0.01)
                self.assertGreater(plan["scale"], 0)
                cards = plan["cards"]
                self.assertEqual(cards["cpu"]["h"], cards["ram"]["h"])
                self.assertEqual(cards["cpu"]["y"], cards["ram"]["y"])
                self.assertEqual(cards["gpu"]["h"], cards["storage"]["h"])
                self.assertEqual(cards["gpu"]["y"], cards["storage"]["y"])
                for name, a in cards.items():
                    self.assertGreater(a["w"], 0)
                    self.assertGreater(a["h"], 0)
                    self.assertLessEqual(a["x"] + a["w"], plan["width"] + 0.01)
                    self.assertLessEqual(a["y"] + a["h"], plan["height"] + 0.01)
                    for other, b in cards.items():
                        if name >= other:
                            continue
                        overlap_x = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
                        overlap_y = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
                        self.assertFalse(overlap_x > 0.01 and overlap_y > 0.01, (name, other))

    def test_empty_optional_sections_leave_no_placeholder_cards(self):
        snapshot = {
            "software": [],
            "gpu": {},
            "disks": [{"model": "SSD"}],
            "network": {},
            "weather": {},
        }
        plan = calculate((67, 32, 1299, 736), snapshot, 5)
        self.assertNotIn("software", plan["cards"])
        self.assertNotIn("gpu", plan["cards"])
        self.assertNotIn("network", plan["cards"])
        self.assertNotIn("weather", plan["cards"])
        self.assertGreater(plan["cards"]["storage"]["w"], plan["cards"]["cpu"]["w"] * 2)
        self.assertEqual(plan["cards"]["calendar"]["y"], plan["cards"]["system"]["h"] + plan["gap"])

    def test_invalid_areas_rejected(self):
        for area in [(0, 0, 0, 10), (0, 0, 10, -1), (0, 0, float("nan"), 20)]:
            with self.assertRaises(ValueError):
                calculate(area)
