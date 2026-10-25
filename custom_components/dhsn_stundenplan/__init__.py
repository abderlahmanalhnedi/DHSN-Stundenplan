"""Unofficial read-only DHSN timetable integration for Home Assistant."""

import asyncio
import logging
import re
from datetime import timedelta
from urllib.parse import urlencode

from aiohttp import ClientError, ClientTimeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import BASE_URL, CONF_GROUP, DOMAIN
from .parse import parse_html

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.CALENDAR]
MAX_RESPONSE_BYTES = 3_000_000
UPDATE_INTERVAL = timedelta(hours=1)


class TimetableCoordinator(DataUpdateCoordinator):
    """Fetch a group's timetable at a considerate rate."""

    def __init__(self, hass: HomeAssistant, group: str):
        super().__init__(
            hass,
            _LOGGER,
            name=f"DHSN Stundenplan {group}",
            update_interval=UPDATE_INTERVAL,
        )
        self.group = group
        self.url = BASE_URL + "?" + urlencode(
            {"akttyp": "1", "aktwert": group, "legendefach": "on"}
        )

    async def _async_update_data(self):
        """Fetch and parse; never automatically retry aggressively."""
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(
                self.url,
                timeout=ClientTimeout(total=25),
                allow_redirects=False,
            ) as response:
                response.raise_for_status()
                if response.content_length and response.content_length > MAX_RESPONSE_BYTES:
                    raise ValueError("Timetable response exceeds size limit")
                raw = await response.content.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise ValueError("Timetable response exceeds size limit")
                html = raw.decode(response.charset or "utf-8", errors="replace")
            return await self.hass.async_add_executor_job(parse_html, html, self.group)
        except (ClientError, asyncio.TimeoutError, OSError, UnicodeError, ValueError) as exc:
            raise UpdateFailed(f"Timetable update failed: {type(exc).__name__}") from exc


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a native calendar for the configured seminar group."""
    group = entry.data[CONF_GROUP]
    if not re.fullmatch(r"[A-Za-z0-9_-]{2,30}", group):
        raise ConfigEntryNotReady("Invalid seminar group format")
    coordinator = TimetableCoordinator(hass, group)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the calendar cleanly."""
    result = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if result:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return result
