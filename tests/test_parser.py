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

    def test_cache_round_trip_lecture_and_timestamp(self):
        from datetime import datetime, timezone
        events = MOD.parse_html(HTML, "test-1")
        stamp = datetime(2026, 11, 8, 11, 0, tzinfo=timezone.utc)
        saved = MOD.encode_cached_timetable("test-1", stamp, events)
        actual_stamp, restored = MOD.decode_cached_timetable(saved, "test-1")
        self.assertEqual(actual_stamp, stamp)
        self.assertEqual(restored, events)

    def test_cache_valid_empty_timetable(self):
        from datetime import datetime, timezone
        stamp = datetime(2026, 11, 8, 11, 0, tzinfo=timezone.utc)
        saved = MOD.encode_cached_timetable("test-1", stamp, [])
        actual_stamp, restored = MOD.decode_cached_timetable(saved, "test-1")
        self.assertEqual(actual_stamp, stamp)
        self.assertEqual(restored, [])

    def test_cache_round_trip_all_day_holiday(self):
        from datetime import datetime, timezone
        html = HTML.replace('class="Vorlesung"', 'class="Feiertag"')
        events = MOD.parse_html(html, "test-1")
        stamp = datetime(2026, 11, 8, 11, 0, tzinfo=timezone.utc)
        saved = MOD.encode_cached_timetable("test-1", stamp, events)
        _, restored = MOD.decode_cached_timetable(saved, "test-1")
        self.assertEqual(restored, events)

    def test_cache_rejects_wrong_group_and_malformed_data(self):
        from datetime import datetime, timezone
        stamp = datetime(2026, 11, 8, 11, 0, tzinfo=timezone.utc)
        saved = MOD.encode_cached_timetable(
            "test-1", stamp, MOD.parse_html(HTML, "test-1")
        )
        with self.assertRaises(ValueError):
            MOD.decode_cached_timetable(saved, "another-group")
        saved["events"][0]["start"] = "not-a-date"
        with self.assertRaises(ValueError):
            MOD.decode_cached_timetable(saved, "test-1")

    def test_cache_rejects_naive_timestamp(self):
        from datetime import datetime, timezone
        stamp = datetime(2026, 11, 8, 11, 0, tzinfo=timezone.utc)
        saved = MOD.encode_cached_timetable("test-1", stamp, [])
        saved["last_successful_sync"] = "2026-11-08T11:00:00"
        with self.assertRaises(ValueError):
            MOD.decode_cached_timetable(saved, "test-1")

    def test_cache_rejects_naive_event_and_invalid_duration(self):
        from datetime import datetime, timezone
        stamp = datetime(2026, 11, 8, 11, 0, tzinfo=timezone.utc)
        saved = MOD.encode_cached_timetable(
            "test-1", stamp, MOD.parse_html(HTML, "test-1")
        )
        saved["events"][0]["end"] = "2026-11-09T09:15:00"
        with self.assertRaises(ValueError):
            MOD.decode_cached_timetable(saved, "test-1")
        saved["events"][0]["end"] = saved["events"][0]["start"]
        with self.assertRaises(ValueError):
            MOD.decode_cached_timetable(saved, "test-1")

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
