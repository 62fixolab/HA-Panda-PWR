# Copyright (c) 2026 FixoLab
"""Config flow for PandaPWR integration in Home Assistant."""

import voluptuous as vol
from homeassistant import config_entries

from .api import PandaPWRApi
from .const import DOMAIN


class PandaPWRConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PandaPWR."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step for setting up the integration."""
        errors = {}
        if user_input:
            ip_address = user_input["ip_address"]
            api = PandaPWRApi(ip_address)
            if await api.test_connection():
                return self.async_create_entry(title="Panda PWR", data=user_input)
            errors["base"] = "cannot_connect"
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("ip_address"): str}),
            errors=errors,
        )
