# Copyright (c) 2026 FixoLab
"""API client for interacting with PandaPWR devices."""

import aiohttp
import async_timeout

from .const import MAX_COUNTDOWN_SECONDS

HTTP_OK = 200


class PandaPWRApi:
    """API client for PandaPWR devices."""

    def __init__(self, ip_address: str) -> None:
        """Initialize the API client."""
        self._base_url = f"http://{ip_address}"
        self._session = aiohttp.ClientSession()

    async def test_connection(self) -> bool:
        """Test if the connection to the device can be established."""
        try:
            async with (
                async_timeout.timeout(10),
                self._session.get(f"{self._base_url}/update_ele_data") as response,
            ):
                return response.status == HTTP_OK
        except (aiohttp.ClientError, TimeoutError):
            return False

    async def get_data(self) -> dict:
        """Fetch data from the device."""
        try:
            async with (
                async_timeout.timeout(10),
                self._session.get(f"{self._base_url}/update_ele_data") as response,
            ):
                return await response.json()
        except (aiohttp.ClientError, TimeoutError):
            return {}

    async def set_power_state(self, state: int) -> bool:
        """Set power state (0 for off, 1 for on) using RAW payload."""
        payload = f"power={state}"
        try:
            async with (
                async_timeout.timeout(10),
                self._session.post(f"{self._base_url}/set", data=payload) as response,
            ):
                return response.status == HTTP_OK
        except (aiohttp.ClientError, TimeoutError):
            return False

    async def set_usb_state(self, state: int) -> bool:
        """Set USB state (0 for off, 1 for on) using RAW payload."""
        payload = f"usb={state}"
        try:
            async with (
                async_timeout.timeout(10),
                self._session.post(f"{self._base_url}/set", data=payload) as response,
            ):
                return response.status == HTTP_OK
        except (aiohttp.ClientError, TimeoutError):
            return False

    async def do_factory_reset(self) -> bool:
        """Perform a factory reset on the device."""
        payload = "factory=1"
        try:
            async with (
                async_timeout.timeout(10),
                self._session.post(f"{self._base_url}/set", data=payload) as response,
            ):
                return response.status == HTTP_OK
        except (aiohttp.ClientError, TimeoutError):
            return False

    async def reset_energy_usage(self) -> bool:
        """Reset energy usage statistics on the device."""
        payload = "reset_usage=1"
        try:
            async with (
                async_timeout.timeout(10),
                self._session.post(f"{self._base_url}/set", data=payload) as response,
            ):
                return response.status == HTTP_OK
        except (aiohttp.ClientError, TimeoutError):
            return False

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

        payload = f"countdown_ctl={state}"
        try:
            async with (
                async_timeout.timeout(10),
                self._session.post(f"{self._base_url}/set", data=payload) as response,
            ):
                return response.status == HTTP_OK
        except (aiohttp.ClientError, TimeoutError):
            return False

    async def set_countdown_timer(self, seconds: int) -> bool:
        """Set countdown timer in seconds using RAW payload. Max 86400 seconds."""
        if seconds < 0 or seconds > MAX_COUNTDOWN_SECONDS:
            return False

        payload = f"countdown_val={seconds}"
        try:
            async with (
                async_timeout.timeout(10),
                self._session.post(f"{self._base_url}/set", data=payload) as response,
            ):
                return response.status == HTTP_OK
        except (aiohttp.ClientError, TimeoutError):
            return False

    async def set_auto_poweroff(self, state: int) -> bool:
        """Set auto power-off state (0 for off, 1 for on) using RAW payload."""
        payload = f"auto_poweroff={state}"
        try:
            async with (
                async_timeout.timeout(10),
                self._session.post(f"{self._base_url}/set", data=payload) as response,
            ):
                return response.status == HTTP_OK
        except (aiohttp.ClientError, TimeoutError):
            return False

    async def send_multi_command(self, commands: dict) -> bool:
        """Send multiple commands in a single RAW payload."""
        payload = "&".join(f"{key}={value}" for key, value in commands.items())
        try:
            async with (
                async_timeout.timeout(10),
                self._session.post(f"{self._base_url}/set", data=payload) as response,
            ):
                return response.status == HTTP_OK
        except (aiohttp.ClientError, TimeoutError):
            return False
