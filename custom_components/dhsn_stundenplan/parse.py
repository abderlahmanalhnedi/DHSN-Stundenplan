"""Parse timetable HTML into timezone-aware lecture events."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import re
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

BERLIN = ZoneInfo("Europe/Berlin")
TIME_RE = re.compile(r"\b(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\b")
WEEK_RE = re.compile(
    r"\bvom\s+(\d{1,2}\.\d{1,2}\.\d{4})\s*-\s*(\d{1,2}\.\d{1,2}\.\d{4})",
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
            continue
        weeks_seen += 1
        week_start = datetime.strptime(week_match.group(1), "%d.%m.%Y").date()
        if week_start.weekday() != 0:
            raise ValueError("Timetable week does not start on Monday")

        rows = table.find_all("tr", recursive=False)
        slots: list[tuple[time, time]] = []
        for row in rows[1:]:
            heading = row.find("th", recursive=False)
            time_match = TIME_RE.search(heading.get_text(" ", strip=True)) if heading else None
            if not time_match:
                raise ValueError("Time range missing")
            slots.append(
                (time.fromisoformat(time_match.group(1)),
                 time.fromisoformat(time_match.group(2)))
            )
        if not slots:
            continue

        occupied = [0] * 5
        for row_number, row in enumerate(rows[1:]):
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
