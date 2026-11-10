"""Unofficial read-only DHSN timetable integration for Home Assistant."""

import logging
import re
from datetime import date, datetime, timedelta, timezone

from urllib.error import HTTPError, URLError
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import build_timetable_url, fetch_timetable
from .const import CONF_GROUP, DOMAIN
from .parse import (
    BERLIN,
    decode_cached_timetable,
    encode_cached_timetable,
    merge_weekly_events,
    parse_html,
    require_nonempty_timetable,
    require_requested_week,
    require_sufficient_weeks,
    rolling_anchor,
    safe_validation_reason,
    week_starts_in_html,
    week_table_counts,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.CALENDAR, Platform.SENSOR]
MIN_EXPECTED_WEEK_TABLES = 4  # Safety threshold based on an observed 8-week source.
UPDATE_INTERVAL = timedelta(hours=1)
STORAGE_VERSION = 1
# One HTTP GET per hour, rotated through overlapping six-week anchors.
# Nine windows span up to roughly 13 months without increasing request rate.
WINDOW_COUNT = 9
WINDOW_STEP_WEEKS = 6


class TimetableCoordinator(DataUpdateCoordinator):
    """Poll one seminar group's timetable and retain its last good snapshot."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        group = entry.data[CONF_GROUP]
        super().__init__(
            hass,
            _LOGGER,
            name=f"DHSN Stundenplan {group}",
            update_interval=UPDATE_INTERVAL,
        )
        self.group = group
        self.last_successful_sync: datetime | None = None
        self.last_response_week_tables: int | None = None
        self.last_response_recognized_weeks: int | None = None
        self.last_response_event_count: int | None = None
        self.last_http_status: int | None = None
        self.last_failure_reason: str | None = None
        self.last_requested_date: date | None = None
        self.next_window_index = 0
        self.scan_base_monday: date | None = None
        self.completed_windows: set[int] = set()
        # Scope the private local cache to this individual config entry.
        self.store = Store(
            hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}", private=True
        )

    async def async_restore_cache(self) -> None:
        """Restore a validated snapshot before attempting a network refresh."""
        try:
            saved = await self.store.async_load()
            if saved is None:
                return
            restored_at, events = decode_cached_timetable(saved, self.group)
            if not events:
                # Older releases could overwrite a good snapshot with an
                # incorrectly parsed empty page. Do not trust that snapshot
                # as evidence of a successful timetable download.
                self.data = []
                _LOGGER.warning(
                    "Cached DHSN timetable is empty; awaiting a valid refresh"
                )
                return
        except Exception as exc:  # Storage can fail due to unreadable files.
            _LOGGER.warning(
                "Could not restore cached DHSN timetable (%s)",
                type(exc).__name__,
            )
            return

        self.data = events
        self.last_successful_sync = restored_at
        # Metadata added in 0.2.9; restore older event-only snapshots unchanged.
        if isinstance(saved, dict):
            try:
                stored_base = date.fromisoformat(saved.get("scan_base_monday", ""))
                next_index = saved.get("next_window_index")
                completed = saved.get("completed_windows", [])
                if (
                    type(next_index) is int
                    and 0 <= next_index < WINDOW_COUNT
                    and isinstance(completed, list)
                    and all(type(i) is int and 0 <= i < WINDOW_COUNT for i in completed)
                ):
                    self.scan_base_monday = stored_base
                    self.next_window_index = next_index
                    self.completed_windows = set(completed)
            except (ValueError, TypeError):
                pass
        _LOGGER.debug("Restored cached DHSN timetable: %s events", len(events))

    async def _async_update_data(self):
        """Refresh one dated source window, safely merging overlapping weeks.

        A single hourly request rotates through nine dated windows. Existing
        November events stay present when the January window is refreshed.
        """
        today = datetime.now(BERLIN).date()
        monday = rolling_anchor(today, 0)
        if self.scan_base_monday != monday:
            self.scan_base_monday = monday
            self.next_window_index = 0
            self.completed_windows.clear()

        index = self.next_window_index
        self.next_window_index = (index + 1) % WINDOW_COUNT
        anchor = rolling_anchor(today, index, WINDOW_STEP_WEEKS)
        self.last_requested_date = anchor

        self.last_response_week_tables = None
        self.last_response_recognized_weeks = None
        self.last_response_event_count = None
        self.last_http_status = None
        self.last_failure_reason = None

        try:
            # Date navigation is exposed by the public web interface:
            # ?AktTyp=1&LegendeFach&Datum=4.1.2027&AktWert=3sp26-1
            # Keep the established 1/hour request cadence.
            url = build_timetable_url(self.group, anchor)
            fetched = await self.hass.async_add_executor_job(fetch_timetable, url)
            self.last_http_status = fetched.http_status
            html = fetched.html

            tables, recognized = await self.hass.async_add_executor_job(
                week_table_counts, html
            )
            self.last_response_week_tables = tables
            self.last_response_recognized_weeks = recognized
            require_sufficient_weeks(
                tables, recognized, MIN_EXPECTED_WEEK_TABLES
            )
            weeks = await self.hass.async_add_executor_job(
                week_starts_in_html, html
            )
            # Reject HTTP 200 if the server ignored the requested date.
            require_requested_week(weeks, anchor)
            incoming = await self.hass.async_add_executor_job(
                parse_html, html, self.group
            )
            self.last_response_event_count = len(incoming)
            require_nonempty_timetable(incoming)
            # Only replace the source weeks in the newly retrieved period.
            events = merge_weekly_events(
                self.data or [], incoming, weeks, today
            )
        except ValueError as exc:
            self.last_failure_reason = safe_validation_reason(exc)
            raise UpdateFailed(
                f"Timetable validation failed: {self.last_failure_reason}"
            ) from exc
        except (HTTPError, URLError, TimeoutError, OSError, UnicodeError) as exc:
            self.last_failure_reason = type(exc).__name__
            if isinstance(exc, HTTPError):
                self.last_http_status = exc.code
            raise UpdateFailed(
                f"Timetable request failed: {self.last_failure_reason}"
            ) from exc

        refreshed_at = datetime.now(timezone.utc)
        self.last_successful_sync = refreshed_at
        self.completed_windows.add(index)
        try:
            snapshot = encode_cached_timetable(self.group, refreshed_at, events)
            snapshot["scan_base_monday"] = monday.isoformat()
            snapshot["next_window_index"] = self.next_window_index
            snapshot["completed_windows"] = sorted(self.completed_windows)
            await self.store.async_save(snapshot)
        except Exception as exc:
            _LOGGER.warning(
                "Could not save cached DHSN timetable (%s)",
                type(exc).__name__,
            )
        _LOGGER.debug(
            "Merged DHSN timetable: %s cached events, %s source events, "
            "%s/%s weeks, scanned windows %s/%s",
            len(events),
            self.last_response_event_count,
            recognized,
            tables,
            len(self.completed_windows),
            WINDOW_COUNT,
        )
        return events


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up calendar and sync sensors, including during source outages."""
    group = entry.data[CONF_GROUP]
    if not re.fullmatch(r"[A-Za-z0-9_-]{2,30}", group):
        raise ConfigEntryNotReady("Invalid seminar group format")
    coordinator = TimetableCoordinator(hass, entry)
    await coordinator.async_restore_cache()
    # First refresh is non-fatal only when we have a saved valid snapshot.
    await coordinator.async_refresh()
    if coordinator.data is None:
        raise ConfigEntryNotReady(
            "Timetable unavailable and no previously saved timetable exists"
        )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload without discarding the snapshot used after a restart."""
    result = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if result:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return result


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Erase cached timetable content when the integration is removed."""
    store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}", private=True)
    await store.async_remove()
