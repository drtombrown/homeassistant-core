"""Rako Light integration."""

# from pprint import pp

# import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

# import homeassistant.helpers.config_validation as cv
# from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN
from .coordinator import RakoLightCoordinator

PLATFORMS: list[Platform] = [Platform.LIGHT]


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry[RakoLightCoordinator]
) -> bool:
    """Set up Rako Light from a Config entry (Config Flow)."""

    # set up coordinator
    coordinator = RakoLightCoordinator(hass, config_entry)

    # fetch initial data
    # await coordinator.async_refresh()
    await coordinator.async_config_entry_first_refresh()

    hub_status = await coordinator.get_hub_status()

    device_registry = dr.async_get(hass)

    # add hub as device to device registry
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, hub_status.id)},
        connections={(dr.CONNECTION_NETWORK_MAC, hub_status.mac_address)},
        name="Rako Hub",
        model="HUB (Wireless)",
        manufacturer="Rako Controls Ltd",
        sw_version=hub_status.version,
    )

    config_entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, config_entry: ConfigEntry[RakoLightCoordinator]
) -> bool:
    """Unload a config entry."""

    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
