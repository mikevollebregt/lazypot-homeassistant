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

# How a config entry gets its data. Entries from before 1.1.0 have no mode and are cloud.
CONF_MODE = "mode"
MODE_CLOUD = "cloud"
MODE_LOCAL = "local"

# Local mode: every pot in the house POSTs to this one fixed, local-only webhook (the
# firmware has the path compiled in: /api/webhook/lazypot_local). One local entry per HA.
LOCAL_WEBHOOK_ID = "lazypot_local"
LOCAL_UNIQUE_ID = "local"

# A pot that has not reported for this long is shown as unavailable. Normal sleep (night plus
# a long interval) stays well below it, so sleeping is never a fault. Same as the pot's MQTT
# expire_after.
LOCAL_STALE_HOURS = 36

SIGNAL_LOCAL_NEW_POT = "lazypot_local_new_pot_{}"
# A local report was taken over by a cloud entry that knows the same pot (arg: device id).
SIGNAL_LOCAL_CLAIMED = "lazypot_local_claimed"
SIGNAL_LOCAL_UPDATE = "lazypot_local_update_{}_{}"
