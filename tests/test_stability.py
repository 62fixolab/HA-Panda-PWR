# Copyright (c) 2026 FixoLab
"""Stability tests: polling load, outages and corrupt replies."""

import logging
import random

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.panda_pwr.const import DOMAIN

from .conftest import FakePandaPWR, make_entry, setup_entry


async def poll(hass: HomeAssistant, entry_id: str = "panda") -> None:
    """Run one polling cycle, as the 30 s update interval does."""
    await hass.config_entries.async_get_entry(entry_id).runtime_data.async_refresh()
    await hass.async_block_till_done()


def states(hass: HomeAssistant) -> dict[str, str]:
    """Return the state of every Panda PWR entity, keyed by unique ID suffix."""
    registry = er.async_get(hass)
    return {
        entity.unique_id.rsplit(":", 1)[-1].split("_", 1)[-1]: hass.states.get(
            entity.entity_id
        ).state
        for entity in registry.entities.values()
        if entity.platform == DOMAIN and hass.states.get(entity.entity_id)
    }


def errors(caplog: pytest.LogCaptureFixture) -> list[logging.LogRecord]:
    """Return real errors, ignoring the expected unavailability message."""
    return [
        record
        for record in caplog.records
        if record.levelno >= logging.ERROR
        and not record.getMessage().startswith("Error fetching panda_pwr data")
        and "transport creation" not in record.getMessage()
    ]


async def test_one_request_per_cycle(hass: HomeAssistant, device: FakePandaPWR) -> None:
    """All entities share a single request per polling cycle."""
    await setup_entry(hass, make_entry(device))
    device.gets = 0
    for _ in range(5):
        await poll(hass)
    assert device.gets == 5


async def test_outage_marks_unavailable_and_recovers(
    hass: HomeAssistant, device: FakePandaPWR
) -> None:
    """While offline every entity is unavailable, never a fake zero."""
    await setup_entry(hass, make_entry(device))
    before = states(hass)
    port = device.port

    await device.stop()
    await poll(hass)
    assert set(states(hass).values()) == {STATE_UNAVAILABLE}

    await device.start(port)
    await poll(hass)
    await poll(hass)
    assert states(hass) == before


@pytest.mark.parametrize("mode", ["http500", "bad_json", "html", "list_json"])
async def test_corrupt_reply(
    hass: HomeAssistant,
    device: FakePandaPWR,
    caplog: pytest.LogCaptureFixture,
    mode: str,
) -> None:
    """A broken reply makes entities unavailable without raising exceptions."""
    await setup_entry(hass, make_entry(device))
    caplog.clear()
    device.mode = mode
    await poll(hass)
    assert states(hass)["power"] == STATE_UNAVAILABLE
    device.mode = "ok"
    await poll(hass)
    assert not errors(caplog)


async def test_soak_random_faults(
    hass: HomeAssistant, device: FakePandaPWR, caplog: pytest.LogCaptureFixture
) -> None:
    """500 cycles (about 4 hours of polling) with random faults and outages."""
    rnd = random.Random(42)  # noqa: S311
    entry = await setup_entry(hass, make_entry(device))
    caplog.clear()
    port = device.port
    offline = False
    modes = ["ok"] * 14 + ["http500", "bad_json", "html", "list_json", "offline"]
    for _ in range(500):
        mode = rnd.choice(modes)
        if mode == "offline":
            if not offline:
                await device.stop()
                offline = True
        else:
            if offline:
                await device.start(port)
                offline = False
            device.mode = mode
        await poll(hass)
    if offline:
        await device.start(port)
    device.mode = "ok"
    await poll(hass)

    assert entry.state is ConfigEntryState.LOADED
    assert not errors(caplog)
    assert states(hass)["power"] == "96.6"
