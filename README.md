<p align="center">
  <img src="https://raw.githubusercontent.com/mikevollebregt/lazypot-homeassistant/master/custom_components/lazypot/brand/logo@2x.png" alt="LazyPot" width="220">
</p>

<h1 align="center">LazyPot for Home Assistant</h1>

<p align="center">
  Bring your <a href="https://lazypot.nl">LazyPot</a> self-watering smart plant pots into Home Assistant:
  soil moisture, reservoir level, battery and watering history as native devices and entities.
</p>

<p align="center">
  <a href="https://github.com/mikevollebregt/lazypot-homeassistant/releases"><img alt="Release" src="https://img.shields.io/github/v/release/mikevollebregt/lazypot-homeassistant"></a>
  <a href="https://hacs.xyz"><img alt="HACS Default" src="https://img.shields.io/badge/HACS-Default-41BDF5.svg"></a>
  <a href="https://github.com/mikevollebregt/lazypot-homeassistant/actions/workflows/hassfest.yml"><img alt="hassfest" src="https://github.com/mikevollebregt/lazypot-homeassistant/actions/workflows/hassfest.yml/badge.svg"></a>
  <a href="https://github.com/mikevollebregt/lazypot-homeassistant/actions/workflows/hacs.yml"><img alt="HACS validation" src="https://github.com/mikevollebregt/lazypot-homeassistant/actions/workflows/hacs.yml/badge.svg"></a>
  <img alt="Home Assistant 2024.11+" src="https://img.shields.io/badge/Home%20Assistant-2024.11%2B-18BCF2">
  <a href="https://github.com/mikevollebregt/lazypot-homeassistant/blob/master/LICENSE"><img alt="License: MIT" src="https://img.shields.io/github/license/mikevollebregt/lazypot-homeassistant"></a>
</p>

---

LazyPot is a complete smart plant pot: it measures the soil, waters the plant
from its own built-in reservoir and tells you when the reservoir needs a
refill. No loose sensors, tubing or DIY pump build. This integration makes
every LazyPot on your account show up in Home Assistant, so you can put your
plants on your dashboards and use them in automations like any other device.

- Website: [lazypot.nl](https://lazypot.nl)
- Smart home overview: [lazypot.nl/smart-home](https://lazypot.nl/smart-home)
- Public roadmap and voting: [lazypot.nl/roadmap](https://lazypot.nl/roadmap)

## Status

- **Latest release:** [v1.0.3](https://github.com/mikevollebregt/lazypot-homeassistant/releases/latest)
- **Verified:** End to end in a real Home Assistant instance against a real LazyPot account and real pots
- **Install via HACS:** Yes, listed in the HACS default store since 2026-11-02 ([hacs/default#11984](https://github.com/hacs/default/pull/11984))
- **Control from Home Assistant:** Not yet, read-only today ([planned](https://lazypot.nl/roadmap/home-assistant-watering-controls))
- **Local control:** Not yet, cloud polling today ([researching](https://lazypot.nl/roadmap/local-control))

See the [changelog](https://github.com/mikevollebregt/lazypot-homeassistant/blob/master/CHANGELOG.md) for what changed in each release and the
[roadmap](https://github.com/mikevollebregt/lazypot-homeassistant/blob/master/ROADMAP.md) for what comes next.

## What you get

Each pot becomes one Home Assistant device with these entities:

| Entity | Type | Description |
| --- | --- | --- |
| Moisture | Sensor (%) | Soil moisture measured by the pot |
| Water level | Sensor (%) | How full the built-in reservoir is |
| Battery | Sensor (%) | Battery level |
| Last watered | Sensor (timestamp) | When the pot last watered the plant |
| Last seen | Sensor (timestamp) | When the pot last reported in |
| Online | Binary sensor (connectivity) | On when the pot reported within the last 24 hours |
| Low battery | Binary sensor (battery) | On when the battery is below 20% |
| Low water | Binary sensor (problem) | On when the reservoir is below 15% |

## Installation

### HACS (recommended)

[![Open your Home Assistant instance and open this repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mikevollebregt&repository=lazypot-homeassistant&category=integration)

Or manually in HACS:

1. Open HACS in Home Assistant and search for **LazyPot**.
2. Open it and click **Download**.
3. Restart Home Assistant.

You no longer need to add it as a custom repository. If you did that before
the store listing, it keeps working and you can leave it as is.

### Manual

1. Download the [latest release](https://github.com/mikevollebregt/lazypot-homeassistant/releases/latest).
2. Copy `custom_components/lazypot` into the `custom_components` folder of your Home Assistant configuration directory.
3. Restart Home Assistant.

## Configuration

1. Sign in on [lazypot.nl](https://lazypot.nl) and open your account's
   [API tokens](https://lazypot.nl/account/integrations) page.
2. Create a token and copy it. It is shown only once.
3. In Home Assistant go to **Settings, Devices & services, Add integration**
   and search for **LazyPot**.
4. Paste the token. All pots on your account are added as devices.

[![Open your Home Assistant instance and start setting up LazyPot.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=lazypot)

If you revoke the token later, Home Assistant asks you to re-authenticate the
LazyPot integration. Paste a new token there and your devices, entities and
history are kept.

## Example automation

Get a phone notification when a reservoir needs refilling. Replace the entity
and notify service with your own.

```yaml
automation:
  - alias: "LazyPot reservoir almost empty"
    triggers:
      - trigger: state
        entity_id: binary_sensor.living_room_pot_low_water
        to: "on"
    actions:
      - action: notify.mobile_app_your_phone
        data:
          title: "Refill your LazyPot"
          message: "The reservoir of {{ trigger.to_state.attributes.friendly_name }} is almost empty."
```

A ready-made dashboard card and importable automation blueprints are
[planned](https://lazypot.nl/roadmap/home-assistant-dashboard-card-and-blueprints).
Share your own dashboards and automations in
[Show and tell](https://github.com/mikevollebregt/lazypot-homeassistant/discussions/categories/show-and-tell).

## How it works, data and privacy

- **Cloud polling.** The integration reads your pots from the LazyPot
  smart-home API (`smarthome.lazypot.nl`) every 10 minutes. Automations and
  dashboards then run locally in your Home Assistant. Local control without
  the cloud is on the [roadmap](https://lazypot.nl/roadmap/local-control).
- **Pots report about twice a day.** LazyPot runs on a battery and sleeps
  between check-ins, so readings update roughly every 12 hours. Faster polling
  would not give fresher data.
- **Read-only, scoped token.** The integration never sees your LazyPot
  password. It uses a separate token that can only read your pots, and that
  you can revoke at any time from your account.
- **Your data only.** The API only returns pots that belong to the account
  the token was created for.

Developers who want to build their own integration can use the same API:
[smarthome.lazypot.nl/swagger](https://smarthome.lazypot.nl/swagger/index.html).

## Roadmap

The roadmap is public and you can vote and comment on every item on
[lazypot.nl/roadmap](https://lazypot.nl/roadmap). Home Assistant items:

| Item | Status |
| --- | --- |
| [Home Assistant integration](https://lazypot.nl/roadmap/home-assistant-integration) | Shipped |
| [More developer API endpoints](https://lazypot.nl/roadmap/more-developer-api-endpoints) | Shipped |
| [Official HACS store listing](https://lazypot.nl/roadmap/hacs-default-store-listing) | Shipped |
| [Dashboard card and automation blueprints](https://lazypot.nl/roadmap/home-assistant-dashboard-card-and-blueprints) | Planned |
| [Control watering from Home Assistant](https://lazypot.nl/roadmap/home-assistant-watering-controls) | Planned |
| [Local control (no cloud needed)](https://lazypot.nl/roadmap/local-control) | Planned, researching |
| [Real-time WebSocket API](https://lazypot.nl/roadmap/real-time-websocket-api) | Planned |

More detail in [ROADMAP.md](https://github.com/mikevollebregt/lazypot-homeassistant/blob/master/ROADMAP.md).

## Support and feedback

- Found a bug? [Open an issue](https://github.com/mikevollebregt/lazypot-homeassistant/issues/new/choose).
- Question or idea? Start a [discussion](https://github.com/mikevollebregt/lazypot-homeassistant/discussions).
- Want a feature? Vote or comment on the [roadmap](https://lazypot.nl/roadmap), or suggest a new item there.

To share logs, enable debug logging first:

```yaml
logger:
  logs:
    custom_components.lazypot: debug
```

Never post your token in an issue or discussion.

## About

Hi, I'm Mike. I design and build LazyPot myself in the Netherlands: the pot,
the electronics, the firmware, the app and the servers behind it. I wanted my
plants to be part of my smart home without a pile of separate sensors, tubes
and YAML, and this integration is how LazyPot becomes a proper Home Assistant
device.

If something does not work, the person who built it is the one reading your
issue. More about me and how LazyPot was made:
[lazypot.nl/meet-the-maker](https://lazypot.nl/meet-the-maker).

## Development

Contributions are welcome, see [CONTRIBUTING.md](https://github.com/mikevollebregt/lazypot-homeassistant/blob/master/CONTRIBUTING.md).

```bash
# Link the integration into a local or throwaway Home Assistant config directory
ln -s "$(pwd)/custom_components/lazypot" <ha_config_dir>/custom_components/lazypot
```

Every push runs [hassfest](https://github.com/mikevollebregt/lazypot-homeassistant/blob/master/.github/workflows/hassfest.yml) and the
[HACS action](https://github.com/mikevollebregt/lazypot-homeassistant/blob/master/.github/workflows/hacs.yml).

## License

[MIT](https://github.com/mikevollebregt/lazypot-homeassistant/blob/master/LICENSE)
