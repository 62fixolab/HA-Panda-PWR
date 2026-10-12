# Copyright (c) 2026 FixoLab
"""API client for interacting with PandaPWR devices."""

import asyncio

import aiohttp

from .const import MAX_COUNTDOWN_SECONDS

HTTP_OK = 200
REQUEST_TIMEOUT = 10


class PandaPWRError(Exception):
    """Raised when the device cannot be reached or returns an invalid reply."""


class PandaPWRApi:
    """API client for PandaPWR devices."""

    def __init__(self, session: aiohttp.ClientSession, ip_address: str) -> None:
        """Initialize the API client with Home Assistant's shared session."""
        self._session = session
        self._base_url = f"http://{ip_address}"

    async def test_connection(self) -> bool:
        """Test if the connection to the device can be established."""
        try:
            await self.get_data()
        except PandaPWRError:
            return False
        return True

    async def get_data(self) -> dict:
        """Fetch data from the device, raising PandaPWRError on any failure."""
        try:
            async with (
                asyncio.timeout(REQUEST_TIMEOUT),
                self._session.get(f"{self._base_url}/update_ele_data") as response,
            ):
                if response.status != HTTP_OK:
                    msg = f"Unexpected HTTP status {response.status}"
                    raise PandaPWRError(msg)
                data = await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise PandaPWRError(str(err) or type(err).__name__) from err
        if not isinstance(data, dict):
            msg = f"Unexpected payload type {type(data).__name__}"
            raise PandaPWRError(msg)
        return data

    async def _post(self, payload: str) -> bool:
        """Send a RAW payload to the device and report whether it was accepted."""
        try:
            async with (
                asyncio.timeout(REQUEST_TIMEOUT),
                self._session.post(f"{self._base_url}/set", data=payload) as response,
            ):
                return response.status == HTTP_OK
        except (aiohttp.ClientError, TimeoutError):
            return False

    async def set_power_state(self, state: int) -> bool:
        """Set power state (0 for off, 1 for on) using RAW payload."""
        return await self._post(f"power={state}")

    async def set_usb_state(self, state: int) -> bool:
        """Set USB state (0 for off, 1 for on) using RAW payload."""
        return await self._post(f"usb={state}")

    async def do_factory_reset(self) -> bool:
        """Perform a factory reset on the device."""
        return await self._post("factory=1")

    async def reset_energy_usage(self) -> bool:
        """Reset energy usage statistics on the device."""
        return await self._post("reset_usage=1")

    async def set_countdown_state(self, state: int) -> bool:
        """
        Set countdown timer state using RAW payload.

        0 for stop
        1 for start
        2 for pause by Panda Touch (reserved)
        3 for pause by web
        """
        if state not in range(4):
            return False
        return await self._post(f"countdown_ctl={state}")

    async def set_countdown_timer(self, seconds: int) -> bool:
        """Set countdown timer in seconds using RAW payload. Max 86400 seconds."""
        if seconds < 0 or seconds > MAX_COUNTDOWN_SECONDS:
            return False
        return await self._post(f"countdown_val={seconds}")

    async def set_auto_poweroff(self, state: int) -> bool:
        """Set auto power-off state (0 for off, 1 for on) using RAW payload."""
        return await self._post(f"auto_poweroff={state}")

    async def send_multi_command(self, commands: dict) -> bool:
        """Send multiple commands in a single RAW payload."""
        return await self._post(
            "&".join(f"{key}={value}" for key, value in commands.items())
        )
