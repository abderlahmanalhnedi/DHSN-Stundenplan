"""Conservative single-request timetable downloader.

Only called in Home Assistant's executor; never from the event loop.
The urllib transport matched the complete eight-week response in the user's
November 2026 diagnostic, unlike the aiohttp transport used previously.
"""

from dataclasses import dataclass
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_RESPONSE_BYTES = 3_000_000
TIMEOUT_SECONDS = 25
# Match the request that obtained a complete response in the user's test.
TIMETABLE_HEADERS = {"User-Agent": "Mozilla/5.0"}


@dataclass(frozen=True)
class FetchedTimetable:
    """Minimal safe result. Do not log HTML or request URLs."""

    http_status: int
    html: str


class NoRedirectHandler(HTTPRedirectHandler):
    """Do not follow unexpected redirects or login pages."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_timetable(url: str) -> FetchedTimetable:
    """Perform exactly one HTTPS GET and read bounded HTML."""

    if not url.startswith("https://stundenplan.ba-dresden.de/stundenplan/PlanServlet?"):
        raise ValueError("Unexpected timetable endpoint")

    request = Request(url, headers=TIMETABLE_HEADERS, method="GET")
    opener = build_opener(NoRedirectHandler())
    with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
        status = response.getcode()
        if status != 200:
            raise ValueError("Unexpected timetable HTTP status")

        size = response.headers.get("Content-Length")
        if size is not None and int(size) > MAX_RESPONSE_BYTES:
            raise ValueError("Timetable response exceeds size limit")

        raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("Timetable response exceeds size limit")

        charset = response.headers.get_content_charset() or "utf-8"
        return FetchedTimetable(
            http_status=status,
            html=raw.decode(charset, errors="replace"),
        )
