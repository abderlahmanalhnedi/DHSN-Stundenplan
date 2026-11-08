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

    def test_empty_week_is_rejected_as_successful_update(self):
        empty = HTML.replace('class="Vorlesung"', 'class="Freizeit"')
        self.assertEqual(MOD.week_table_counts(empty), (1, 1))
        events = MOD.parse_html(empty, "test-1")
        self.assertEqual(events, [])
        with self.assertRaisesRegex(ValueError, "No timetable events parsed"):
            MOD.require_nonempty_timetable(events)

    def test_eight_synthetic_weeks_parse_without_network(self):
        from datetime import date, timedelta
        monday = date(2026, 11, 9)
        pages = []
        for i in range(8):
            start = monday + timedelta(weeks=i)
            end = start + timedelta(days=6)
            caption = f"{46+i}. Woche vom {start.day}.{start.month}.{start.year}-{end.day}.{end.month}.{end.year}"
            pages.append(HTML.replace("46. Woche vom 9.11.2026-15.11.2026", caption))
        document = "\n".join(pages)
        self.assertEqual(MOD.week_table_counts(document), (8, 8))
        self.assertEqual(len(MOD.parse_html(document, "test-1")), 8)

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

    def test_rows_nested_in_tbody_are_recognized(self):
        html = HTML.replace(
            '<tr><th>Zeit</th>',
            '<tbody><tr><th>Zeit</th>',
        ).replace('</table>', '</tbody></table>')
        events = MOD.parse_html(html, "test-1")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].summary, "DEMO")

    def test_non_slot_footer_does_not_break_timetable(self):
        html = HTML.replace(
            '</table>',
            '<tr><th>Stand: 08.11.2026</th><td colspan="5">'
            'Hinweis zur Planung</td></tr></table>',
        )
        self.assertEqual(len(MOD.parse_html(html, "test-1")), 1)

    def test_en_dash_time_range(self):
        html = HTML.replace("07:45 - 09:15", "07:45 – 09:15")
        self.assertEqual(len(MOD.parse_html(html, "test-1")), 1)

    def test_lecture_with_missing_time_range_is_rejected(self):
        html = HTML.replace("07:45 - 09:15", "unknown time")
        with self.assertRaisesRegex(ValueError, "Time range missing"):
            MOD.parse_html(html, "test-1")

    def test_empty_result_must_not_overwrite_last_good_data(self):
        empty_events = MOD.parse_html(
            HTML.replace('class="Vorlesung"', 'class="Freizeit"'), "test-1"
        )
        self.assertEqual(empty_events, [])
        with self.assertRaisesRegex(ValueError, "No timetable events parsed"):
            MOD.require_nonempty_timetable(empty_events)

    def test_nonempty_result_passes_validation(self):
        events = MOD.parse_html(HTML, "test-1")
        self.assertIs(MOD.require_nonempty_timetable(events), events)

    def test_empty_result_has_a_safe_error_reason(self):
        self.assertEqual(
            MOD.safe_validation_reason(ValueError("No timetable events parsed")),
            "No timetable events parsed",
        )

    def test_multiple_seminar_weeks_are_parsed(self):
        second = HTML.replace(
            "46. Woche vom 9.11.2026-15.11.2026",
            "47. Woche vom 16.11.2026-22.11.2026",
        )
        combined = HTML + second
        self.assertEqual(len(MOD.parse_html(combined, "test-1")), 2)
        self.assertEqual(MOD.week_table_counts(combined), (2, 2))

    def test_captions_with_en_dash_are_readable(self):
        html = HTML.replace(
            "9.11.2026-15.11.2026", "9.11.2026–15.11.2026"
        )
        self.assertEqual(len(MOD.parse_html(html, "test-1")), 1)

    def test_unknown_week_caption_cannot_be_silently_skipped(self):
        second = HTML.replace(
            "46. Woche vom 9.11.2026-15.11.2026",
            "47. Woche 16.11.2026 bis 22.11.2026",
        )
        with self.assertRaisesRegex(
            ValueError, "Timetable week header not recognized"
        ):
            MOD.parse_html(HTML + second, "test-1")

    def test_shrinking_future_coverage_protected(self):
        from datetime import datetime, timezone
        original = MOD.parse_html(
            HTML.replace(
                "46. Woche vom 9.11.2026-15.11.2026",
                "50. Woche vom 7.12.2026-13.12.2026",
            ),
            "test-1",
        )
        partial = MOD.parse_html(HTML, "test-1")
        now = datetime(2026, 11, 8, 20, 0, tzinfo=timezone.utc)
        self.assertTrue(
            MOD.would_lose_future_coverage(original, partial, now)
        )
        self.assertFalse(
            MOD.would_lose_future_coverage(partial, original, now)
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
