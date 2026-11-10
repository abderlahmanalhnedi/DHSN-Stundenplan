"""Offline tests for the exact single-request urllib transport."""

import importlib.util
import io
from email.message import Message
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

CLIENT = (
    Path(__file__).resolve().parents[1]
    / "custom_components" / "dhsn_stundenplan" / "client.py"
)
SPEC = importlib.util.spec_from_file_location("dhsn_test_client", CLIENT)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

URL = (
    "https://stundenplan.ba-dresden.de/stundenplan/PlanServlet"
    "?akttyp=1&aktwert=test-1&legendefach=on"
)


class FakeResponse:
    def __init__(self, body: bytes, status: int = 200):
        self.stream = io.BytesIO(body)
        self.status = status
        self.headers = Message()
        self.headers["Content-Type"] = "text/html; charset=utf-8"
        self.headers["Content-Length"] = str(len(body))

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def getcode(self):
        return self.status

    def read(self, n):
        return self.stream.read(n)


class TestSingleRequestTransport(unittest.TestCase):
    def test_fetch_returns_html_and_browser_user_agent(self):
        from unittest.mock import Mock
        opener = Mock()
        opener.open.return_value = FakeResponse(b"<table>hello</table>")
        with patch.object(MOD, "build_opener", return_value=opener):
            result = MOD.fetch_timetable(URL)

        self.assertEqual(result.http_status, 200)
        self.assertIn("hello", result.html)
        opener.open.assert_called_once()
        args, kwargs = opener.open.call_args
        self.assertEqual(kwargs["timeout"], MOD.TIMEOUT_SECONDS)
        self.assertEqual(args[0].get_method(), "GET")
        self.assertEqual(
            dict(args[0].header_items()).get("User-agent"), "Mozilla/5.0"
        )

    def test_no_redirects(self):
        self.assertIsNone(
            MOD.NoRedirectHandler().redirect_request(
                None, None, 302, "redirect", {}, "https://example.org/"
            )
        )

    def test_too_large_response_is_rejected(self):
        from unittest.mock import Mock
        opener = Mock()
        opener.open.return_value = FakeResponse(b"x" * (MOD.MAX_RESPONSE_BYTES + 1))
        with patch.object(MOD, "build_opener", return_value=opener):
            with self.assertRaisesRegex(ValueError, "size limit"):
                MOD.fetch_timetable(URL)
        opener.open.assert_called_once()

    def test_non_200_http_response_is_rejected(self):
        from unittest.mock import Mock
        opener = Mock()
        opener.open.return_value = FakeResponse(b"not ready", 206)
        with patch.object(MOD, "build_opener", return_value=opener):
            with self.assertRaisesRegex(ValueError, "HTTP status"):
                MOD.fetch_timetable(URL)

    def test_foreign_endpoint_is_rejected_before_network_access(self):
        with patch.object(MOD, "build_opener") as opener:
            with self.assertRaisesRegex(ValueError, "endpoint"):
                MOD.fetch_timetable("https://example.org/")
            opener.assert_not_called()


if __name__ == "__main__":
    unittest.main()
