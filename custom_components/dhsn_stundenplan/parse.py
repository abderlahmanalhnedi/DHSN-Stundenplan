"""Parse timetable HTML into timezone-aware lecture events."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import re
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

BERLIN = ZoneInfo("Europe/Berlin")
TIME_RE = re.compile(r"\b(\d{1,2}:\d{2})\s*[-–—−]\s*(\d{1,2}:\d{2})\b")
WEEK_RE = re.compile(
    r"\bvom\s+(\d{1,2}\.\d{1,2}\.\d{4})\s*[-–—−]\s*(\d{1,2}\.\d{1,2}\.\d{4})",
    re.I,
)


@dataclass(frozen=True)
class TimetableEvent:
    """A single lesson or all-day holiday."""

    start: date | datetime
    end: date | datetime
    summary: str
    location: str
    description: str


def text_by_class(element, cls):
    node = element.find(class_=cls)
    return node.get_text(" ", strip=True) if node else ""

# Only constant, developer-authored error messages can reach Home Assistant logs.
# Unexpected parser exceptions may contain remote HTML data, so do not log str(exc).
SAFE_VALIDATION_REASONS = frozenset(
    {
        "Timetable response exceeds size limit",
        "Timetable week does not start on Monday",
        "Time range missing",
        "Bad weekday column count",
        "Invalid lecture rowspan",
        "No valid timetable table in response",
        "No timetable events parsed",
        "Timetable week header not recognized",
        "Timetable future coverage unexpectedly shortened",
    }
)


def safe_validation_reason(error: ValueError) -> str:
    """Return a safe diagnostic reason without reflecting response content."""
    reason = str(error)
    if reason in SAFE_VALIDATION_REASONS:
        return reason
    return "Unexpected timetable structure"



def start_as_utc(event: TimetableEvent) -> datetime:
    start = event.start
    if isinstance(start, datetime):
        return start.astimezone(timezone.utc)
    return datetime.combine(start, time.min, BERLIN).astimezone(timezone.utc)


def end_as_utc(event: TimetableEvent) -> datetime:
    end = event.end
    if isinstance(end, datetime):
        return end.astimezone(timezone.utc)
    return datetime.combine(end, time.min, BERLIN).astimezone(timezone.utc)


def parse_html(html: str, group: str) -> list[TimetableEvent]:
    """Read five-day lecture tables; reject login and unexpected pages."""
    soup = BeautifulSoup(html, "html.parser")
    result: list[TimetableEvent] = []
    weeks_seen = 0

    for table in soup.select("table.Plan"):
        caption = table.find("caption")
        week_match = WEEK_RE.search(caption.get_text(" ", strip=True)) if caption else None
        if not week_match:
            # Do not silently skip published weeks if the university changes
            # the week caption's punctuation or layout.
            if caption and re.search(r"\bWoche\b", caption.get_text(" ", strip=True), re.I):
                raise ValueError("Timetable week header not recognized")
            continue
        weeks_seen += 1
        week_start = datetime.strptime(week_match.group(1), "%d.%m.%Y").date()
        if week_start.weekday() != 0:
            raise ValueError("Timetable week does not start on Monday")

        # Some HTML variants wrap table rows in <thead>/<tbody>. Ignore
        # non-slot header/footer rows, but fail if a lesson row lacks a time.
        rows = []
        for child in table.children:
            if getattr(child, "name", None) == "tr":
                rows.append(child)
            elif getattr(child, "name", None) in ("thead", "tbody", "tfoot"):
                rows.extend(child.find_all("tr", recursive=False))

        slots: list[tuple[time, time]] = []
        lecture_rows = []
        for row in rows:
            heading = row.find("th", recursive=False)
            time_match = (
                TIME_RE.search(heading.get_text(" ", strip=True))
                if heading else None
            )
            if not time_match:
                if any(
                    set(cell.get("class", [])) & {"Vorlesung", "Feiertag"}
                    for cell in row.find_all("td", recursive=False)
                ):
                    raise ValueError("Time range missing")
                continue
            slots.append(
                (time.fromisoformat(time_match.group(1)),
                 time.fromisoformat(time_match.group(2)))
            )
            lecture_rows.append(row)
        if not slots:
            continue

        occupied = [0] * 5
        for row_number, row in enumerate(lecture_rows):
            column = 0
            for cell in row.find_all("td", recursive=False):
                while column < 5 and occupied[column] > 0:
                    column += 1
                if column >= 5:
                    raise ValueError("Bad weekday column count")
                rowspan = max(1, int(cell.get("rowspan", 1)))
                colspan = max(1, int(cell.get("colspan", 1)))
                day = week_start + timedelta(days=column)
                classes = cell.get("class", [])

                if "Vorlesung" in classes:
                    if row_number + rowspan > len(slots):
                        raise ValueError("Invalid lecture rowspan")
                    subject = text_by_class(cell, "fach") or cell.get_text(" ", strip=True)
                    lecturer = text_by_class(cell, "dozent")
                    room = text_by_class(cell, "ort")
                    comment = text_by_class(cell, "bemerkung")
                    start = datetime.combine(day, slots[row_number][0], BERLIN)
                    end = datetime.combine(
                        day, slots[row_number + rowspan - 1][1], BERLIN
                    )
                    description = [f"Seminargruppe: {group}"]
                    if lecturer:
                        description.append(f"Dozent: {lecturer}")
                    if comment:
                        description.append(f"Bemerkung: {comment}")
                    result.append(
                        TimetableEvent(
                            start, end, subject, room, "\n".join(description)
                        )
                    )
                elif "Feiertag" in classes:
                    title = cell.get_text(" ", strip=True)
                    result.append(
                        TimetableEvent(
                            day, day + timedelta(days=1),
                            title, "", f"Seminargruppe: {group}"
                        )
                    )

                for c in range(column, min(5, column + colspan)):
                    occupied[c] = rowspan
                column += colspan
            occupied = [max(0, amount - 1) for amount in occupied]

    if not weeks_seen:
        raise ValueError("No valid timetable table in response")
    result.sort(key=start_as_utc)
    return result



def week_table_counts(html: str) -> tuple[int, int]:
    """Count source weekly tables without exposing their HTML or lecturer data."""
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.select("table.Plan")
    recognized = 0
    for table in tables:
        caption = table.find("caption")
        if caption and WEEK_RE.search(caption.get_text(" ", strip=True)):
            recognized += 1
    return len(tables), recognized


def would_lose_future_coverage(
    existing: list[TimetableEvent],
    incoming: list[TimetableEvent],
    now: datetime,
) -> bool:
    """Keep the last good timetable if a smaller response loses future weeks.

    Only protect genuinely future coverage: naturally expired semesters are
    permitted to roll over. This is a conservative heuristic, not proof that
    the university still plans the old events.
    """
    if not existing or not incoming:
        return False
    last_existing = max(end_as_utc(event) for event in existing)
    last_incoming = max(end_as_utc(event) for event in incoming)
    return (
        last_existing > now.astimezone(timezone.utc) + timedelta(days=7)
        and last_incoming + timedelta(days=7) < last_existing
    )


def require_nonempty_timetable(events: list[TimetableEvent]) -> list[TimetableEvent]:
    """Reject silently empty parses instead of treating lost lectures as success.

    This deliberately errs on the side of retaining a visibly stale timetable
    if a genuinely empty semester cannot be distinguished from changed HTML.
    """
    if not events:
        raise ValueError("No timetable events parsed")
    return events


# Last-known-good cache format: only event data, never source HTML or cookies.
MAX_CACHED_EVENTS = 2000
MAX_CACHED_TEXT = 2000


def encode_cached_timetable(
    group: str, refreshed_at: datetime, events: list[TimetableEvent]
) -> dict:
    """Serialize a bounded copy of the last complete successful response."""
    return {
        "group": group,
        "last_successful_sync": refreshed_at.astimezone(timezone.utc).isoformat(),
        "events": [
            {
                "all_day": not isinstance(event.start, datetime),
                "start": event.start.isoformat(),
                "end": event.end.isoformat(),
                "summary": event.summary,
                "location": event.location,
                "description": event.description,
            }
            for event in events[:MAX_CACHED_EVENTS]
        ],
    }


def decode_cached_timetable(
    payload: dict, expected_group: str
) -> tuple[datetime, list[TimetableEvent]]:
    """Reject corrupted/mismatched local cache files without exposing contents."""
    if not isinstance(payload, dict) or payload.get("group") != expected_group:
        raise ValueError("Invalid timetable cache group")
    stamp = payload.get("last_successful_sync")
    if not isinstance(stamp, str):
        raise ValueError("Invalid timetable cache timestamp")
    refreshed_at = datetime.fromisoformat(stamp)
    if refreshed_at.tzinfo is None or refreshed_at.utcoffset() is None:
        raise ValueError("Naive timetable cache timestamp")
    raw_events = payload.get("events")
    if not isinstance(raw_events, list) or len(raw_events) > MAX_CACHED_EVENTS:
        raise ValueError("Invalid timetable cache events")
    events = []
    for raw in raw_events:
        if not isinstance(raw, dict) or type(raw.get("all_day")) is not bool:
            raise ValueError("Invalid timetable cache event")
        fields = ("summary", "location", "description")
        if any(
            not isinstance(raw.get(field), str)
            or len(raw[field]) > MAX_CACHED_TEXT
            for field in fields
        ):
            raise ValueError("Invalid timetable cache text")
        if not isinstance(raw.get("start"), str) or not isinstance(raw.get("end"), str):
            raise ValueError("Invalid timetable cache dates")
        if raw["all_day"]:
            start = date.fromisoformat(raw["start"])
            end = date.fromisoformat(raw["end"])
        else:
            start = datetime.fromisoformat(raw["start"])
            end = datetime.fromisoformat(raw["end"])
            if (
                start.tzinfo is None
                or start.utcoffset() is None
                or end.tzinfo is None
                or end.utcoffset() is None
            ):
                raise ValueError("Naive timetable cache event")
        event = TimetableEvent(
            start, end, raw["summary"], raw["location"], raw["description"]
        )
        if end_as_utc(event) <= start_as_utc(event):
            raise ValueError("Invalid timetable cache duration")
        events.append(event)
    events.sort(key=start_as_utc)
    return refreshed_at.astimezone(timezone.utc), events
