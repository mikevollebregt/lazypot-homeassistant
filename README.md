# LazyPot for Home Assistant

HACS-installable custom integration that brings your LazyPot smart plant
pots into Home Assistant as native devices/entities (soil moisture, battery,
water level, last-watered) so you can build your own dashboards and
automations instead of relying on the LazyPot app.

Status: **validated end-to-end against a live LazyPot account (2026-10-15)**.
The config flow, entities, and derived binary sensors were exercised in a
real Home Assistant instance against production `smarthome.lazypot.nl` using
a real integration token generated from the LazyPot website
(`/account/integrations`): all 15 devices on the account imported correctly
as HA devices (8 entities each), and every sensor/binary_sensor value
(battery, moisture, water level, last-seen, last-watered, online, low-battery,
low-water) matched the live API response exactly. Along the way this test
caught and fixed a real production bug in the backend (`lazypot-smarthome`
commit `ba073f9`): `GET /devices` was 500ing because it queried a
`UserId` column on `LazyPotConnections` that doesn't exist — ownership is
resolved through the `LazyPotConnectionUsers` join table instead, same as
kataskopos' own `GetLazyPotsByUser`. See
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
