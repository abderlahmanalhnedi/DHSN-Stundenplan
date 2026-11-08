"""Offline, synthetic fixture tests; no actual university data."""

import importlib.util
from pathlib import Path
import sys
import unittest

PARSER = (
    Path(__file__).resolve().parents[1]
    / "custom_components" / "dhsn_stundenplan" / "parse.py"
)
SPEC = importlib.util.spec_from_file_location("dhsn_test_parser", PARSER)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

HTML = """<html><table class="Plan">
<caption>46. Woche vom 9.11.2026-15.11.2026</caption>
<tr><th>Zeit</th><th>Mo</th><th>Di</th><th>Mi</th><th>Do</th><th>Fr</th></tr>
<tr><th>07:45 - 09:15</th><td class="Vorlesung">
<span class="fach">DEMO</span><span class="dozent">Prof. Example</span>
<span class="ort">Room 101</span></td><td></td><td></td><td></td><td></td></tr>
</table></html>"""


class TestParser(unittest.TestCase):
    def test_lecture(self):
        events = MOD.parse_html(HTML, "test-1")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].summary, "DEMO")
        self.assertEqual(events[0].location, "Room 101")
        self.assertEqual(events[0].start.hour, 7)
        self.assertEqual(events[0].end.hour, 9)
        self.assertIn("Prof. Example", events[0].description)

    def test_empty_week(self):
        html = HTML.replace('class="Vorlesung"', 'class="Freizeit"')
        self.assertEqual(MOD.parse_html(html, "test-1"), [])

    def test_manifest_declares_parser_dependency(self):
        import json
        manifest = (
            Path(__file__).resolve().parents[1]
            / "custom_components" / "dhsn_stundenplan" / "manifest.json"
        )
        data = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertIn("beautifulsoup4>=4.15.0", data["requirements"])

    def test_safe_validation_reason_for_unknown_values(self):
        self.assertEqual(
            MOD.safe_validation_reason(ValueError("Private html content")),
            "Unexpected timetable structure",
        )

    def test_safe_validation_reason_for_known_values(self):
        self.assertEqual(
            MOD.safe_validation_reason(
                ValueError("No valid timetable table in response")
            ),
            "No valid timetable table in response",
        )

    def test_login_page_rejected(self):
        with self.assertRaises(ValueError):
            MOD.parse_html("<html>Login required</html>", "test-1")

    def test_holiday(self):
        html = HTML.replace('class="Vorlesung"', 'class="Feiertag"')
        events = MOD.parse_html(html, "test-1")
        self.assertEqual(len(events), 1)
        self.assertEqual((events[0].end - events[0].start).days, 1)


if __name__ == "__main__":
    unittest.main()
