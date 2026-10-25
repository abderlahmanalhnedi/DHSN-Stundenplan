"""Read-only calendar entity exposing the upcoming timetable events."""

from datetime import datetime, timezone

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .parse import end_as_utc, start_as_utc


def to_calendar_event(item):
    """Convert a parsed timetable item to a Home Assistant calendar event."""
    return CalendarEvent(
        start=item.start,
        end=item.end,
        summary=item.summary,
        description=item.description,
        location=item.location or None,
    )


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Register the calendar entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DHSNCalendar(coordinator)])


class DHSNCalendar(CoordinatorEntity, CalendarEntity):
    """A calendar for one seminar group."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = f"Stundenplan {coordinator.group}"
        self._attr_unique_id = f"dhsn_stundenplan_{coordinator.group}"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the current or next scheduled event."""
        now = datetime.now(timezone.utc)
        for item in self.coordinator.data or []:
            if end_as_utc(item) > now:
                return to_calendar_event(item)
        return None

    async def async_get_events(self, hass, start_date, end_date):
        """Return events in the requested range, chronologically."""
        start_utc = start_date.astimezone(timezone.utc)
        end_utc = end_date.astimezone(timezone.utc)
        return [
            to_calendar_event(item)
            for item in (self.coordinator.data or [])
            if end_as_utc(item) > start_utc and start_as_utc(item) < end_utc
        ]
