# Copyright (c) 2026 FixoLab
"""Entity tests: names, values and every write action."""

from datetime import timedelta

import pytest
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.panda_pwr.const import DOMAIN

from .conftest import FakePandaPWR, make_entry, setup_entry


def entity_id(hass: HomeAssistant, device: FakePandaPWR, domain: str, key: str) -> str:
    """Return the entity ID of an entity by its unique ID suffix."""
    result = er.async_get(hass).async_get_entity_id(
        domain, DOMAIN, f"pandapwr_{device.host}_{key}"
    )
    assert result, f"{domain} {key} not registered"
    return result


def state(hass: HomeAssistant, device: FakePandaPWR, domain: str, key: str) -> str:
    """Return the current state of an entity by its unique ID suffix."""
    return hass.states.get(entity_id(hass, device, domain, key)).state


async def call(
    hass: HomeAssistant, domain: str, service: str, target: str, **data: object
) -> None:
    """Call a service and wait for every resulting state change."""
    await hass.services.async_call(
        domain, service, {"entity_id": target, **data}, blocking=True
    )
    await hass.async_block_till_done()


async def settle(hass: HomeAssistant) -> None:
    """Let the read-back that follows a write run."""
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=4))
    await hass.async_block_till_done()


async def test_names_and_values(hass: HomeAssistant, device: FakePandaPWR) -> None:
    """Entities use translated names and numeric values, even for text fields."""
    await setup_entry(hass, make_entry(device))
    power = hass.states.get(entity_id(hass, device, "sensor", "power"))
    assert power.name == "Panda PWR Power"
    assert power.state == "96.6"
    assert state(hass, device, "sensor", "countdown_state") == "stopped"
    assert state(hass, device, "sensor", "auto_poweroff") == "0"
    assert state(hass, device, "number", "countdown_time") == "0"


async def test_destructive_buttons_disabled_by_default(
    hass: HomeAssistant, device: FakePandaPWR
) -> None:
    """Factory and energy resets need to be enabled on purpose."""
    await setup_entry(hass, make_entry(device))
    registry = er.async_get(hass)
    for key in ("factory_reset_button", "energy_usage_reset_button"):
        entry = registry.async_get(entity_id(hass, device, "button", key))
        assert entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION


@pytest.mark.parametrize(
    ("key", "field", "data_key"),
    [("power_switch", "power", "power_state"), ("usb_switch", "usb", "usb_state")],
)
async def test_output_switches(
    hass: HomeAssistant, device: FakePandaPWR, key: str, field: str, data_key: str
) -> None:
    """Switching updates the device, the switch and its binary sensor at once."""
    await setup_entry(hass, make_entry(device))
    switch = entity_id(hass, device, "switch", key)
    binary = entity_id(hass, device, "binary_sensor", data_key)

    for service, value, expected in (
        ("turn_on", 1, STATE_ON),
        ("turn_off", 0, STATE_OFF),
        ("turn_on", 1, STATE_ON),
    ):
        await call(hass, "switch", service, switch)
        assert device.posts[-1] == f"{field}={value}"
        assert hass.states.get(switch).state == expected
        assert hass.states.get(binary).state == expected
        await settle(hass)
        assert hass.states.get(switch).state == expected


async def test_refused_write_raises(hass: HomeAssistant, device: FakePandaPWR) -> None:
    """A command the device rejects surfaces as an error and changes nothing."""
    await setup_entry(hass, make_entry(device))
    switch = entity_id(hass, device, "switch", "power_switch")
    device.mode = "http500"
    with pytest.raises(HomeAssistantError):
        await call(hass, "switch", "turn_off", switch)
    assert hass.states.get(switch).state == STATE_ON


async def test_countdown_number(hass: HomeAssistant, device: FakePandaPWR) -> None:
    """The countdown time is sent in seconds and validated against the 24 h limit."""
    await setup_entry(hass, make_entry(device))
    number = entity_id(hass, device, "number", "countdown_time")
    await call(hass, "number", "set_value", number, value=120)
    assert device.posts[-1] == "countdown_val=120"
    assert hass.states.get(number).state == "120"
    with pytest.raises(ServiceValidationError):
        await call(hass, "number", "set_value", number, value=90000)


async def test_shutdown_timer(hass: HomeAssistant, device: FakePandaPWR) -> None:
    """Start, pause, resume and stop send the official web UI commands."""
    await setup_entry(hass, make_entry(device))
    timer = entity_id(hass, device, "switch", "shutdown_timer")
    number = entity_id(hass, device, "number", "countdown_time")
    countdown_state = entity_id(hass, device, "sensor", "countdown_state")

    await call(hass, "number", "set_value", number, value=600)
    await call(hass, "switch", "turn_on", timer)
    assert device.posts[-1] == "countdown_val=600&countdown_ctl=1&auto_poweroff=1"
    assert hass.states.get(timer).state == STATE_ON
    assert hass.states.get(countdown_state).state == "running"

    await call(
        hass,
        "button",
        "press",
        entity_id(hass, device, "button", "pause_shutdown_timer"),
    )
    assert device.posts[-1] == "countdown_ctl=3&auto_poweroff=1"
    assert hass.states.get(countdown_state).state == "paused"
    assert hass.states.get(timer).state == STATE_ON

    await call(
        hass,
        "button",
        "press",
        entity_id(hass, device, "button", "resume_shutdown_timer"),
    )
    assert device.posts[-1] == "countdown_ctl=1&auto_poweroff=1"
    assert hass.states.get(countdown_state).state == "running"

    await call(hass, "switch", "turn_off", timer)
    assert device.posts[-1] == "countdown_ctl=0&auto_poweroff=0"
    assert hass.states.get(timer).state == STATE_OFF
    await settle(hass)
    assert hass.states.get(countdown_state).state == "stopped"


async def test_shutdown_timer_powers_on_and_defaults(
    hass: HomeAssistant, device: FakePandaPWR
) -> None:
    """With the output off and no duration, it powers on and uses 30 minutes."""
    device.state["power_state"] = 0
    await setup_entry(hass, make_entry(device))
    await call(
        hass, "switch", "turn_on", entity_id(hass, device, "switch", "shutdown_timer")
    )
    assert device.posts[-1] == (
        "countdown_val=1800&countdown_ctl=1&auto_poweroff=1&power=1"
    )
    assert state(hass, device, "switch", "power_switch") == STATE_ON


async def test_auto_poweroff_switch(hass: HomeAssistant, device: FakePandaPWR) -> None:
    """Auto power-off toggles the firmware flag."""
    await setup_entry(hass, make_entry(device))
    switch = entity_id(hass, device, "switch", "auto_poweroff_switch")
    await call(hass, "switch", "turn_on", switch)
    assert device.posts[-1] == "auto_poweroff=1"
    assert hass.states.get(switch).state == STATE_ON
    await call(hass, "switch", "turn_off", switch)
    assert device.posts[-1] == "auto_poweroff=0"


async def test_destructive_buttons_when_enabled(
    hass: HomeAssistant, device: FakePandaPWR
) -> None:
    """Once enabled, the reset buttons send the official commands."""
    entry = make_entry(device)
    await setup_entry(hass, entry)
    registry = er.async_get(hass)
    for key in ("energy_usage_reset_button", "factory_reset_button"):
        registry.async_update_entity(
            entity_id(hass, device, "button", key), disabled_by=None
        )
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    await call(
        hass,
        "button",
        "press",
        entity_id(hass, device, "button", "energy_usage_reset_button"),
    )
    assert device.posts[-1] == "reset_usage=1"
    assert state(hass, device, "sensor", "energy_usage") == "0.0"

    await call(
        hass,
        "button",
        "press",
        entity_id(hass, device, "button", "factory_reset_button"),
    )
    assert device.posts[-1] == "factory=1"
