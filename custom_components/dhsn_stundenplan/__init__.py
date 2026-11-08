"""Unofficial read-only DHSN timetable integration for Home Assistant."""

import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from aiohttp import ClientError, ClientTimeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import BASE_URL, CONF_GROUP, DOMAIN
from .parse import (
    decode_cached_timetable,
    encode_cached_timetable,
    parse_html,
    require_nonempty_timetable,
    safe_validation_reason,
    week_table_counts,
    would_lose_future_coverage,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.CALENDAR, Platform.SENSOR]
MAX_RESPONSE_BYTES = 3_000_000
UPDATE_INTERVAL = timedelta(hours=1)
STORAGE_VERSION = 1


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
        # Scope the private local cache to this individual config entry.
        self.store = Store(
            hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}", private=True
        )
        self.url = BASE_URL + "?" + urlencode(
            {"akttyp": "1", "aktwert": group, "legendefach": "on"}
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
        _LOGGER.debug("Restored cached DHSN timetable: %s events", len(events))

    async def _async_update_data(self):
        """Fetch and parse, never replacing a valid cache with failed responses."""
        self.last_response_week_tables = None
        self.last_response_recognized_weeks = None
        self.last_response_event_count = None
        self.last_http_status = None
        self.last_failure_reason = None
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(
                self.url,
                timeout=ClientTimeout(total=25),
                allow_redirects=False,
            ) as response:
                self.last_http_status = response.status
                response.raise_for_status()
                if response.content_length and response.content_length > MAX_RESPONSE_BYTES:
                    raise ValueError("Timetable response exceeds size limit")
                raw = await response.content.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise ValueError("Timetable response exceeds size limit")
                html = raw.decode(response.charset or "utf-8", errors="replace")

            tables, recognized = await self.hass.async_add_executor_job(
                week_table_counts, html
            )
            self.last_response_week_tables = tables
            self.last_response_recognized_weeks = recognized
            events = await self.hass.async_add_executor_job(parse_html, html, self.group)
            self.last_response_event_count = len(events)
            # A syntactically valid table with no recognized events can be a
            # changed university page; it must never replace good calendar data.
            require_nonempty_timetable(events)
            if would_lose_future_coverage(
                self.data or [], events, datetime.now(timezone.utc)
            ):
                raise ValueError("Timetable future coverage unexpectedly shortened")
        except ValueError as exc:
            self.last_failure_reason = safe_validation_reason(exc)
            raise UpdateFailed(
                f"Timetable validation failed: {self.last_failure_reason}"
            ) from exc
        except (ClientError, asyncio.TimeoutError, OSError, UnicodeError) as exc:
            self.last_failure_reason = type(exc).__name__
            raise UpdateFailed(
                f"Timetable request failed: {self.last_failure_reason}"
            ) from exc

        # Only a complete valid parse can replace the old snapshot.
        refreshed_at = datetime.now(timezone.utc)
        self.last_successful_sync = refreshed_at
        try:
            snapshot = encode_cached_timetable(self.group, refreshed_at, events)
            await self.store.async_save(snapshot)
        except Exception as exc:  # A disk error must not hide fresh data.
            _LOGGER.warning(
                "Could not save cached DHSN timetable (%s)", type(exc).__name__
            )
        _LOGGER.debug(
            "Parsed DHSN timetable: %s events from %s/%s recognized week tables",
            len(events),
            self.last_response_recognized_weeks,
            self.last_response_week_tables,
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
