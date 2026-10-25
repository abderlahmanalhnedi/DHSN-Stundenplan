"""One-field setup flow: the seminar group."""

import re

import voluptuous as vol
from homeassistant import config_entries

from .const import CONF_GROUP, DOMAIN


class DHSNTimetableConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure the group without user credentials."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            group = str(user_input[CONF_GROUP]).strip()
            if not re.fullmatch(r"[A-Za-z0-9_-]{2,30}", group):
                errors[CONF_GROUP] = "invalid_group"
            else:
                await self.async_set_unique_id(group.lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"DHSN Stundenplan {group}",
                    data={CONF_GROUP: group},
                )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_GROUP): str}),
            errors=errors,
        )
