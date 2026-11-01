# Roadmap

The source of truth for the LazyPot roadmap is
[lazypot.nl/roadmap](https://lazypot.nl/roadmap). Every item there can be voted
on and commented on, and you can suggest new items. Votes and comments directly
influence what gets built next. This file summarises the Home Assistant side.

Last updated: 2026-11-01.

## Shipped

- **Home Assistant integration** (v1.0.0, 2026-10-15).
  Every pot as a device with moisture, water level, battery, last watered,
  last seen, online, low battery and low water entities. Verified end to end
  in a real Home Assistant instance against a real account.
  [Roadmap item](https://lazypot.nl/roadmap/home-assistant-integration)
- **Re-authentication flow** (v1.0.1 and v1.0.2, 2026-10-25).
  A revoked token can be replaced from the Home Assistant UI, the entry is
  tied to your LazyPot account instead of the token, and duplicate accounts
  are blocked. Requested during the HACS review.
- **Developer API** for your own integrations: device list, device detail,
  reading history and online status.
  [API docs](https://smarthome.lazypot.nl/swagger/index.html),
  [roadmap item](https://lazypot.nl/roadmap/more-developer-api-endpoints)

## In progress

- **Official HACS store listing.** Submitted as
  [hacs/default#11984](https://github.com/hacs/default/pull/11984), all
  automated checks pass, waiting for the final maintainer review. Until then,
  install it as a HACS custom repository.
  [Roadmap item](https://lazypot.nl/roadmap/hacs-default-store-listing)

## Planned

- **Dashboard card and automation blueprints.** A ready-made dashboard card
  and one-click blueprints for: reservoir almost empty, battery low, pot
  offline, plant too dry and an away-mode summary.
  [Roadmap item](https://lazypot.nl/roadmap/home-assistant-dashboard-card-and-blueprints)
- **Control watering from Home Assistant.** Water now with a hard maximum
  dose, and pause or resume automatic watering. Because the pot sleeps
  between check-ins to save battery, commands are carried out at the next
  check-in and the entity shows that a command is pending.
  [Roadmap item](https://lazypot.nl/roadmap/home-assistant-watering-controls)
- **Real-time WebSocket API.** Push updates instead of polling.
  [Roadmap item](https://lazypot.nl/roadmap/real-time-websocket-api)

## Researching

- **Local control (no cloud needed).** Comparing a local API or MQTT, an
  ESPHome-compatible firmware mode, Zigbee and Matter. Some options may need a
  new hardware or firmware revision. Findings will be posted on the roadmap
  item before a choice is made, so please share what you would prefer.
  [Roadmap item](https://lazypot.nl/roadmap/local-control)

## Not planned right now

- Local control for the current hardware without a firmware update. The
  current pots only talk HTTPS to the LazyPot cloud.
