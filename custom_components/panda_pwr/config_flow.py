# Copyright (c) 2026 FixoLab
"""Config flow for PandaPWR integration in Home Assistant."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PandaPWRApi, PandaPWRError
from .const import CONF_DEVICE_ID, CONF_IP_ADDRESS, DOMAIN, legacy_device_id


class PandaPWRConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PandaPWR."""

    VERSION = 1

    async def _async_probe(self, ip_address: str) -> str | None:
        """
        Check the device answers and return its unique access point SSID.

        Raises PandaPWRError when the device cannot be reached; returns None
        when it answers but does not report an SSID.
        """
        api = PandaPWRApi(async_get_clientsession(self.hass), ip_address)
        await api.get_data()
        try:
            state = await api.get_state()
        except PandaPWRError:
            return None
        return state.get("ap_ssid") or None

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step for setting up the integration."""
        errors = {}
        if user_input:
            ip_address = user_input[CONF_IP_ADDRESS].strip()
            self._async_abort_entries_match({CONF_IP_ADDRESS: ip_address})
            try:
                ap_ssid = await self._async_probe(ip_address)
            except PandaPWRError:
                errors["base"] = "cannot_connect"
            else:
                if ap_ssid:
                    await self.async_set_unique_id(ap_ssid)
                    # Same device at a new IP: update the existing entry instead.
                    self._abort_if_unique_id_configured(
                        updates={CONF_IP_ADDRESS: ip_address}
                    )
                return self.async_create_entry(
                    title="Panda PWR",
                    data={
                        CONF_IP_ADDRESS: ip_address,
                        CONF_DEVICE_ID: legacy_device_id(ip_address),
                    },
                )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_IP_ADDRESS): str}),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """Change the IP address while keeping every entity and its history."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        errors = {}
        if user_input:
            ip_address = user_input[CONF_IP_ADDRESS].strip()
            try:
                ap_ssid = await self._async_probe(ip_address)
            except PandaPWRError:
                errors["base"] = "cannot_connect"
            else:
                if entry.unique_id and ap_ssid and ap_ssid != entry.unique_id:
                    return self.async_abort(reason="wrong_device")
                return self.async_update_reload_and_abort(
                    entry,
                    data={**entry.data, CONF_IP_ADDRESS: ip_address},
                    reason="reconfigure_successful",
                )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_IP_ADDRESS, default=entry.data[CONF_IP_ADDRESS]
                    ): str
                }
            ),
            errors=errors,
        )
