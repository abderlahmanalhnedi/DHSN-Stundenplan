"""Constants for the DHSN Stundenplan integration."""

DOMAIN = "dhsn_stundenplan"
CONF_GROUP = "group"
BASE_URL = "https://stundenplan.ba-dresden.de/stundenplan/PlanServlet"

# Match a regular browser request when retrieving publicly visible timetable pages.
# Identified by a live comparison: a minimal browser UA returned eight weeks,
# while the default aiohttp UA returned only three. No cookies or login headers.
TIMETABLE_HEADERS = {"User-Agent": "Mozilla/5.0"}
