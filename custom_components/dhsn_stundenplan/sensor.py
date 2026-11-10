"""Diagnostic sensors for DHSN timetable synchronization."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Provide status and last successful download time."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            DHSNSyncStatusSensor(coordinator),
            DHSNLastSuccessfulSyncSensor(coordinator),
        ]
    )


class DHSNSyncStatusSensor(CoordinatorEntity, SensorEntity):
    """Report temporary source outages while keeping events visible."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = f"Stundenplan {coordinator.group} Sync-Status"
        self._attr_unique_id = f"dhsn_stundenplan_{coordinator.group}_sync_status"

    @property
    def available(self) -> bool:
        """An unsuccessful poll is a reportable state, not unavailability."""
        return True

    @property
    def native_value(self) -> str:
        """Report whether current displayed data was freshly verified."""
        if self.coordinator.last_successful_sync is None:
            return "no_data"
        return "up_to_date" if self.coordinator.last_update_success else "stale"

    @property
    def icon(self) -> str:
        return "mdi:cloud-check" if self.native_value == "up_to_date" else "mdi:cloud-alert"

    @property
    def extra_state_attributes(self):
        return {
            "last_successful_sync": (
                self.coordinator.last_successful_sync.isoformat()
                if self.coordinator.last_successful_sync
                else None
            ),
            "event_count": len(self.coordinator.data or []),
            "last_response_event_count": self.coordinator.last_response_event_count,
            "last_requested_date": (
                self.coordinator.last_requested_date.isoformat()
                if self.coordinator.last_requested_date else None
            ),
            "completed_date_windows": len(self.coordinator.completed_windows),
            "total_date_windows": 9,
            "next_date_window": self.coordinator.next_window_index,

            "last_http_status": self.coordinator.last_http_status,
            "last_failure_reason": self.coordinator.last_failure_reason,
            "last_response_week_tables": self.coordinator.last_response_week_tables,
            "last_response_recognized_weeks": (
                self.coordinator.last_response_recognized_weeks
            ),
        }


class DHSNLastSuccessfulSyncSensor(CoordinatorEntity, SensorEntity):
    """Timestamp of the most recent successful timetable refresh."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = (
            f"Stundenplan {coordinator.group} Letzte erfolgreiche Synchronisierung"
        )
        self._attr_unique_id = (
            f"dhsn_stundenplan_{coordinator.group}_last_successful_sync"
        )

    @property
    def available(self) -> bool:
        return self.coordinator.last_successful_sync is not None

    @property
    def native_value(self):
        return self.coordinator.last_successful_sync
