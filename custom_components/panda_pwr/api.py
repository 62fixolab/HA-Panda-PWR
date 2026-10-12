# Copyright (c) 2026 FixoLab
"""API client for interacting with PandaPWR devices."""

import asyncio
import contextlib

import aiohttp

from .const import (
    COUNTDOWN_PAUSED,
    COUNTDOWN_RUNNING,
    COUNTDOWN_STOPPED,
    MAX_COUNTDOWN_SECONDS,
)

HTTP_OK = 200
REQUEST_TIMEOUT = 10

# The firmware reports some of these as strings ("0"), others as numbers.
INT_FIELDS = (
    "power_state",
    "usb_state",
    "countdown",
    "countdown_state",
    "auto_poweroff",
)
FLOAT_FIELDS = ("voltage", "current", "power", "ele")


class PandaPWRError(Exception):
    """Raised when the device cannot be reached or returns an invalid reply."""


def _normalize(data: dict) -> dict:
    """Convert the numeric fields the firmware sends as text into numbers."""
    for fields, cast in ((INT_FIELDS, int), (FLOAT_FIELDS, float)):
        for key in fields:
            if key in data:
                with contextlib.suppress(TypeError, ValueError):
                    data[key] = (
                        cast(float(data[key])) if cast is int else cast(data[key])
                    )
    return data


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

    async def _get_json(self, path: str) -> dict:
        """GET a JSON object from the device, raising PandaPWRError on any failure."""
        try:
            async with (
                asyncio.timeout(REQUEST_TIMEOUT),
                self._session.get(f"{self._base_url}{path}") as response,
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

    async def get_data(self) -> dict:
        """Fetch the electrical data and output states."""
        return _normalize(await self._get_json("/update_ele_data"))

    async def get_state(self) -> dict:
        """
        Fetch the device information: firmware, access point and station IP.

        The access point SSID is unique per device; the reply also contains the
        access point password, so never log or expose it unredacted.
        """
        return await self._get_json("/get_state")

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

        The device only counts down while auto power-off is enabled, so start
        the timer together with auto_poweroff=1 (see send_multi_command).
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

    async def start_countdown(self, seconds: int, *, power_on: bool = False) -> bool:
        """Start the shutdown timer the way the official web UI does."""
        if seconds <= 0 or seconds > MAX_COUNTDOWN_SECONDS:
            return False
        commands = {
            "countdown_val": seconds,
            "countdown_ctl": COUNTDOWN_RUNNING,
            "auto_poweroff": 1,
        }
        if power_on:
            commands["power"] = 1
        return await self.send_multi_command(commands)

    async def pause_countdown(self) -> bool:
        """Pause the running shutdown timer."""
        return await self.send_multi_command(
            {"countdown_ctl": COUNTDOWN_PAUSED, "auto_poweroff": 1}
        )

    async def resume_countdown(self) -> bool:
        """Resume a paused shutdown timer."""
        return await self.send_multi_command(
            {"countdown_ctl": COUNTDOWN_RUNNING, "auto_poweroff": 1}
        )

    async def stop_countdown(self) -> bool:
        """Stop the shutdown timer."""
        return await self.send_multi_command(
            {"countdown_ctl": COUNTDOWN_STOPPED, "auto_poweroff": 0}
        )
