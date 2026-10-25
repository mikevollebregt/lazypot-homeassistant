"""The LazyPot integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LazyPotApiClient, LazyPotApiError, is_account_id
from .const import CONF_API_TOKEN, CONF_BASE_URL, DEFAULT_API_BASE_URL, DOMAIN
from .coordinator import LazyPotCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    client = LazyPotApiClient(
        session,
        api_token=entry.data[CONF_API_TOKEN],
        base_url=entry.data.get(CONF_BASE_URL, DEFAULT_API_BASE_URL),
    )
    coordinator = LazyPotCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    await _async_migrate_unique_id(hass, entry, client)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_migrate_unique_id(
    hass: HomeAssistant, entry: ConfigEntry, client: LazyPotApiClient
) -> None:
    """Re-key entries from before 1.0.2 (token prefix) on the stable account id.

    Best effort: if the account endpoint is unavailable, keep the old id and
    retry on the next setup instead of failing the whole integration.
    """
    if is_account_id(entry.unique_id):
        return
    try:
        account_id = await client.async_get_account_id()
    except LazyPotApiError as err:
        _LOGGER.debug("Could not migrate LazyPot unique_id yet: %s", err)
        return
    if hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, account_id):
        # Another entry already covers this account (duplicate added with a
        # second token before 1.0.2); leave this one as is rather than
        # creating two entries with the same unique_id.
        return
    hass.config_entries.async_update_entry(entry, unique_id=account_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded
