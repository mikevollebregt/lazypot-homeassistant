# Security policy

## Supported versions

Only the latest release receives fixes. Please update before reporting.

## Reporting a vulnerability

Please do not report security problems in public issues or discussions.

Report them privately through
[GitHub's private vulnerability reporting](https://github.com/mikevollebregt/lazypot-homeassistant/security/advisories/new).
This covers the integration itself and the LazyPot smart-home API it uses
(`smarthome.lazypot.nl`).

You can expect a first response within a few days. I will keep you updated
while the issue is investigated and fixed, and credit you in the release notes
if you want.

## If your token leaked

Revoke it right away on your account's
[API tokens page](https://lazypot.nl/account/integrations), create a new one
and paste it into Home Assistant when it asks you to re-authenticate. Tokens
are read-only: they cannot change pot settings, your account or your password.
