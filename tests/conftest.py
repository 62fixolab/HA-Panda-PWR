# Copyright (c) 2026 FixoLab
"""Shared fixtures: a simulated Panda PWR with fault injection."""

import asyncio
import json
import sys
from collections.abc import AsyncGenerator
from pathlib import Path
from urllib.parse import parse_qsl

import pytest
import pytest_homeassistant_custom_component
from aiohttp import web
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

# The plugin ships its own `custom_components` package for its test config;
# expose this repository's integration through it so Home Assistant finds it.
_TESTING_CONFIG = Path(pytest_homeassistant_custom_component.__file__).parent / (
    "testing_config"
)
sys.path.insert(0, str(_TESTING_CONFIG))
import custom_components  # noqa: E402

_REPO_COMPONENTS = str(Path(__file__).parents[1] / "custom_components")
if _REPO_COMPONENTS not in custom_components.__path__:
    custom_components.__path__.append(_REPO_COMPONENTS)

from custom_components.panda_pwr.const import (  # noqa: E402
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    DOMAIN,
)

pytest_plugins = ["pytest_homeassistant_custom_component"]

AP_SSID = "PandaPWR_TEST01"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,  # noqa: ARG001
    socket_enabled: None,  # noqa: ARG001
) -> None:
    """Load custom integrations and allow the simulated device's sockets."""
    return


class FakePandaPWR:
    """
    HTTP firmware of a Panda PWR.

    `mode` injects a fault on every reply: "ok", "http500", "bad_json",
    "html", "list_json" or "slow". `stop()` takes the device offline.
    """

    def __init__(self, ap_ssid: str | None = AP_SSID) -> None:
        """Start from an idle device whose output is on."""
        self.mode = "ok"
        self.gets = 0
        self.posts: list[str] = []
        self.ap_ssid = ap_ssid
        # Mixed strings and numbers, like the real firmware.
        self.state = {
            "countdown_state": 0,
            "auto_poweroff": "0",
            "countdown": "0",
            "voltage": 230,
            "current": 0.42,
            "power": 96.6,
            "power_state": 1,
            "usb_state": 0,
            "ele": 12.345,
        }
        self.port: int | None = None
        self._runner: web.AppRunner | None = None

    @property
    def host(self) -> str:
        """Return the address the integration should use."""
        return f"127.0.0.1:{self.port}"

    async def _update_ele_data(self, _request: web.Request) -> web.Response:
        self.gets += 1
        return await self._reply(json.dumps(self.state))

    async def _get_state(self, _request: web.Request) -> web.Response:
        if self.ap_ssid is None:
            return web.Response(status=404)
        return await self._reply(
            json.dumps(
                {
                    "fw_version": "V1.0.0 Aug 20 2024 19:56:17",
                    "connected": "1",
                    "ap_ssid": self.ap_ssid,
                    "ap_pwd": "987654321",
                    "sta_ip": "127.0.0.1",
                }
            )
        )

    async def _set(self, request: web.Request) -> web.Response:
        body = await request.text()
        self.posts.append(body)
        if self.mode == "ok":
            self._apply(dict(parse_qsl(body)))
        return await self._reply("ok")

    def _apply(self, commands: dict) -> None:
        mapping = {
            "power": "power_state",
            "usb": "usb_state",
            "countdown_val": "countdown",
            "countdown_ctl": "countdown_state",
            "auto_poweroff": "auto_poweroff",
        }
        for key, value in commands.items():
            if key in mapping:
                self.state[mapping[key]] = int(value)
            elif key == "reset_usage":
                self.state["ele"] = 0.0

    async def _reply(self, body: str) -> web.Response:
        if self.mode == "ok":
            return web.Response(text=body, content_type="application/json")
        if self.mode == "http500":
            return web.Response(status=500, text="error")
        if self.mode == "bad_json":
            return web.Response(text="{not json", content_type="application/json")
        if self.mode == "html":
            return web.Response(text="<html>busy</html>", content_type="text/html")
        if self.mode == "list_json":
            return web.Response(text="[]", content_type="application/json")
        if self.mode == "slow":
            await asyncio.sleep(15)
            return web.Response(text=body, content_type="application/json")
        raise RuntimeError(self.mode)

    async def start(self, port: int = 0) -> None:
        """Serve the firmware endpoints on 127.0.0.1."""
        app = web.Application()
        app.router.add_get("/update_ele_data", self._update_ele_data)
        app.router.add_get("/get_state", self._get_state)
        app.router.add_post("/set", self._set)
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, "127.0.0.1", port)
        await site.start()
        self.port = site._server.sockets[0].getsockname()[1]  # noqa: SLF001

    async def stop(self) -> None:
        """Take the device offline (connections are refused)."""
        if self._runner:
            await self._runner.cleanup()
            self._runner = None


@pytest.fixture
async def device() -> AsyncGenerator[FakePandaPWR]:
    """Return a running simulated Panda PWR."""
    fake = FakePandaPWR()
    await fake.start()
    yield fake
    await fake.stop()


def make_entry(
    fake: FakePandaPWR, entry_id: str = "panda", **kwargs: object
) -> MockConfigEntry:
    """Build a config entry for the simulated device as 1.3+ creates it."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Panda PWR",
        data={
            CONF_IP_ADDRESS: fake.host,
            CONF_DEVICE_ID: f"pandapwr_{fake.host}",
        },
        entry_id=entry_id,
        **kwargs,
    )


async def setup_entry(hass: HomeAssistant, entry: MockConfigEntry) -> MockConfigEntry:
    """Add and set up an entry, with the services the tests call."""
    await async_setup_component(hass, "homeassistant", {})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry
