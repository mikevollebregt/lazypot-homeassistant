# LazyPot for Home Assistant

HACS-installable custom integration that brings your LazyPot smart plant
pots into Home Assistant as native devices/entities (soil moisture, battery,
water level, last-watered) so you can build your own dashboards and
automations instead of relying on the LazyPot app.

Status: scaffold — not yet functional against a live LazyPot account. See
[`custom_components/lazypot/`](custom_components/lazypot/) for the
in-progress implementation.

## Installation (once published)

1. HACS → Integrations → search "LazyPot" (or add this repo as a custom
   repository while unpublished: HACS → Integrations → ⋮ → Custom
   repositories → paste this repo URL, category "Integration").
2. Home Assistant → Settings → Devices & Services → Add Integration →
   "LazyPot".
3. Paste the integration token generated from your LazyPot account
   (website/app → account settings → "Generate Home Assistant token" —
   not your LazyPot login password).

## What this is NOT

- Not local control — this polls the LazyPot cloud API (`cloud_polling`
  `iot_class`) through a dedicated, access-limited endpoint. Automations
  and dashboards you build in HA still run entirely locally once the data
  is in HA; only the underlying telemetry fetch is cloud-based.
- Not a login integration — it never accepts your LazyPot account
  email/password. Only a narrow, revocable, read-only token.

## Development

```
# requires a local Home Assistant dev instance; see HA's custom component
# devcontainer docs for a throwaway Docker-based HA to iterate against
ln -s "$(pwd)/custom_components/lazypot" <ha_config_dir>/custom_components/lazypot
```

Validate before every push:

```
pip install homeassistant hacs
python -m script.hassfest   # from an HA core checkout, validates manifest.json/structure
```

## API contract

This integration calls one endpoint, authenticated with a scoped,
revocable, read-only Bearer token (not your LazyPot account password):

```
GET {base_url}/devices
Authorization: Bearer <token>
```

Response: a JSON array of device objects:

```json
[
  {
    "connectionId": 123,
    "name": "Living room pot",
    "moistureLevel": 42.5,
    "batteryLevel": 88.0,
    "waterLevel": 60.0,
    "lastWateredOn": "2026-10-10T08:15:00Z"
  }
]
```

See `custom_components/lazypot/api.py` for the client implementation.
