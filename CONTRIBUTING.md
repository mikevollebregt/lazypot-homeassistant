# Contributing

Thanks for wanting to help. Bug reports, ideas, dashboards and code are all
welcome.

## Before you start

- **Bugs:** open an [issue](https://github.com/mikevollebregt/lazypot-homeassistant/issues/new/choose)
  using the bug report template.
- **Feature ideas:** check the [public roadmap](https://lazypot.nl/roadmap)
  first. If it is there, vote and comment. If not, suggest it there or start a
  [discussion](https://github.com/mikevollebregt/lazypot-homeassistant/discussions/categories/ideas).
- **Larger code changes:** open an issue or discussion first so we can agree
  on the approach before you spend time on it.

## Pull requests

1. Fork the repository and create a branch from `master`.
2. Keep changes focused. One feature or fix per pull request.
3. Follow Home Assistant's
   [integration development guidelines](https://developers.home-assistant.io/docs/creating_component_index).
4. Add every new user-facing string to both `strings.json` and
   `translations/en.json`.
5. Make sure the hassfest and HACS workflows pass on your pull request.
6. Describe what you changed and how you checked it in Home Assistant.

## Local development

Run a throwaway Home Assistant, for example with Docker, and link the
integration into its configuration directory:

```bash
ln -s "$(pwd)/custom_components/lazypot" <ha_config_dir>/custom_components/lazypot
```

You need a LazyPot account with at least one pot and a token from
[your account's API tokens page](https://lazypot.nl/account/integrations). The
API is documented at
[smarthome.lazypot.nl/swagger](https://smarthome.lazypot.nl/swagger/index.html).

Never commit or post a token.
