#!/usr/bin/env python3
"""Safely diagnose public DHSN timetable parsing without dumping source data.

This script makes exactly one read-only HTTPS request and prints aggregated
counts and predefined parser error categories. It neither writes response
HTML to disk nor includes timetable details, tokens, or lecturer names in logs.
"""

import argparse
import importlib.util
from pathlib import Path
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PARSER = ROOT / "custom_components" / "dhsn_stundenplan" / "parse.py"
SPEC = importlib.util.spec_from_file_location("dhsn_diagnostic_parser", PARSER)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

BASE_URL = "https://stundenplan.ba-dresden.de/stundenplan/PlanServlet"
MAX_RESPONSE_BYTES = 3_000_000


def summarize(html: str, group: str) -> None:
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.select("table.Plan")
    print(f"Plan tables: {len(tables)}")
    print(f"Recognized week headings: {MOD.week_table_counts(html)[1]}")
    total_lectures = sum(len(t.select("td.Vorlesung")) for t in tables)
    print(f"Lecture cells in Plan tables: {total_lectures}")
    print()
    print("Week  Lecture cells  Parsed events  Safe parser result")
    print("----  -------------  -------------  ------------------")
    sum_events = 0
    for index, table in enumerate(tables, start=1):
        lecture_count = len(table.select("td.Vorlesung"))
        try:
            parsed = MOD.parse_html(str(table), group)
        except ValueError as exc:
            n_events = "-"
            reason = MOD.safe_validation_reason(exc)
        except Exception as exc:
            n_events = "-"
            reason = f"Unexpected parser exception: {type(exc).__name__}"
        else:
            n_events = len(parsed)
            sum_events += len(parsed)
            reason = "OK"
        print(f"{index:>4}  {lecture_count:>13}  {str(n_events):>13}  {reason}")

    print()
    try:
        all_events = MOD.parse_html(html, group)
    except ValueError as exc:
        print("Full page parse: FAILED -", MOD.safe_validation_reason(exc))
    except Exception as exc:
        print("Full page parse: FAILED -", type(exc).__name__)
    else:
        print("Full page parse: OK,", len(all_events), "events")
    print("Sum of individually parsed weeks:", sum_events)
    print("Diagnostic note: source HTML is not saved or printed.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", required=True)
    args = parser.parse_args()
    import re
    if not re.fullmatch(r"[A-Za-z0-9_-]{2,30}", args.group):
        parser.error("Invalid seminar group format")
    params = urlencode({"akttyp": "1", "aktwert": args.group, "legendefach": "on"})
    req = Request(BASE_URL + "?" + params, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=25) as response:
            status = response.status
            if response.headers.get("Content-Length"):
                if int(response.headers["Content-Length"]) > MAX_RESPONSE_BYTES:
                    raise ValueError("Response exceeds size limit")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ValueError("Response exceeds size limit")
            charset = response.headers.get_content_charset() or "utf-8"
            html = raw.decode(charset, errors="replace")
    except Exception as exc:
        print("Fetch failed:", type(exc).__name__)
        return 1
    print("HTTP status:", status)
    summarize(html, args.group)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
