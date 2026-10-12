"""Constants for the LazyPot integration."""

DOMAIN = "lazypot"

# Base URL of the LazyPot smart-home API.
# Overridable only for local/dev testing (not exposed in the config flow UI).
DEFAULT_API_BASE_URL = "https://smarthome.lazypot.nl/api/v1"

CONF_API_TOKEN = "api_token"
CONF_BASE_URL = "base_url"

# Poll interval: LazyPot devices report in roughly every 12h, so polling
# the API faster than this buys nothing and just adds unnecessary load.
# Keep this well above that floor.
DEFAULT_SCAN_INTERVAL_MINUTES = 10

# Simple low-threshold defaults for the derived binary sensors; not (yet)
# user-configurable from the config flow.
LOW_BATTERY_THRESHOLD = 20
LOW_WATER_THRESHOLD = 15

MANUFACTURER = "LazyPot"
