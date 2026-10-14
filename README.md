# LazyPot for Home Assistant

HACS-installable custom integration that brings your LazyPot smart plant
pots into Home Assistant as native devices/entities (soil moisture, battery,
water level, last-watered) so you can build your own dashboards and
automations instead of relying on the LazyPot app.

Status: code-complete. The config flow and entities (soil moisture,
battery, water level, last-watered) are fully implemented against the
documented API contract below. **Not yet validated end-to-end against a
live LazyPot account** — the backend's token-generation endpoint
(`/api/v1/tokens`) that lets you mint the long-lived token this
integration needs is still being built on the LazyPot side. Once token
generation ships on the LazyPot website, you'll be able to generate a
token from your account there and use it here; until then this
integration cannot be exercised against production. See
[`custom_components/lazypot/`](custom_components/lazypot/) for the
implementation.

## HACS installation

This repo is not yet in the HACS default store. Until it is:

1. HACS → Integrations → ⋮ → Custom repositories → paste this repo's
   URL (`https://github.com/mikevollebregt/lazypot-homeassistant`),
   category "Integration" → Add.
2. HACS → Integrations → search "LazyPot" → Download.
3. Restart Home Assistant.
4. Home Assistant → Settings → Devices & Services → Add Integration →
   "LazyPot".
5. Paste the token from your LazyPot account settings (once token
   generation is available there — not your LazyPot login password).

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
