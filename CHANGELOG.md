# Changelog

All notable changes to this integration are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this
project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.3] - 2026-11-02

### Changed

- LazyPot is now in the HACS default store. The README installation steps
  start with searching for LazyPot in HACS instead of adding a custom
  repository.
- New README with installation buttons, entity overview, example automation,
  privacy notes and the public roadmap.
- Added a roadmap, contributing guide, security policy and issue templates.

## [1.0.2] - 2026-10-25

### Changed

- Config entries are now identified by your LazyPot account instead of part
  of the token. Existing installs migrate automatically on the next start.
- Re-authentication refuses a token from a different LazyPot account.
- Adding the same LazyPot account twice is blocked.

### Fixed

- API requests now time out after 30 seconds instead of hanging.
- A timeout or invalid response no longer prevents the integration from
  loading.

## [1.0.1] - 2026-10-25

### Added

- Re-authentication flow. When the token is revoked or rejected, Home
  Assistant asks for a new token. The existing entry, devices and entities
  are kept.

### Changed

- Removed the empty options flow placeholder.
- Minimum Home Assistant version is now 2024.11.0.

## [1.0.0] - 2026-10-15

First release, verified end to end in a real Home Assistant instance against
a real LazyPot account.

### Added

- Config flow with a scoped, read-only token. Your LazyPot password is never
  used.
- Sensors: moisture, battery, water level, last seen, last watered.
- Binary sensors: online, low battery, low water.
- hassfest and HACS validation on every push.

[Unreleased]: https://github.com/mikevollebregt/lazypot-homeassistant/compare/v1.0.3...HEAD
[1.0.3]: https://github.com/mikevollebregt/lazypot-homeassistant/releases/tag/v1.0.3
[1.0.2]: https://github.com/mikevollebregt/lazypot-homeassistant/releases/tag/v1.0.2
[1.0.1]: https://github.com/mikevollebregt/lazypot-homeassistant/releases/tag/v1.0.1
[1.0.0]: https://github.com/mikevollebregt/lazypot-homeassistant/releases/tag/v1.0.0
