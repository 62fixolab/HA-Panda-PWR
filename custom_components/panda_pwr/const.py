# Copyright (c) 2026 FixoLab
"""Constants for the panda_pwr integration."""

DOMAIN = "panda_pwr"

CONF_IP_ADDRESS = "ip_address"
# Frozen when the entry is created so entity unique IDs survive an IP change.
CONF_DEVICE_ID = "device_id"

MANUFACTURER = "BIGTREETECH"
MODEL = "Panda PWR"

# Maximum countdown timer value in seconds (24 hours)
MAX_COUNTDOWN_SECONDS = 86400
# Duration the official web UI proposes when no countdown is configured
DEFAULT_COUNTDOWN_SECONDS = 1800

# countdown_state values reported by the firmware
COUNTDOWN_STOPPED = 0
COUNTDOWN_RUNNING = 1
COUNTDOWN_PAUSED_BY_PANDA_TOUCH = 2
COUNTDOWN_PAUSED = 3
COUNTDOWN_STATES = {
    COUNTDOWN_STOPPED: "stopped",
    COUNTDOWN_RUNNING: "running",
    COUNTDOWN_PAUSED_BY_PANDA_TOUCH: "paused_by_panda_touch",
    COUNTDOWN_PAUSED: "paused",
}


def legacy_device_id(ip_address: str) -> str:
    """Return the device ID that releases up to 1.2.x derived from the IP."""
    return f"pandapwr_{ip_address}"
