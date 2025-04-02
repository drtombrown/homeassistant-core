"""Rako Light integration."""

# from pprint import pp

import voluptuous as vol

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .coordinator import RakoLightCoordinator

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,  # allow other options not explicitly defined
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Rako Light from a config entry."""

    if DOMAIN in config:
        # set up coordinator
        coordinator = RakoLightCoordinator(hass, host=config[DOMAIN][CONF_HOST])

        # fetch initial data
        await coordinator.async_refresh()

        # save coordinator to hass.data, so that it can be used in other parts of the integration
        hass.data[DOMAIN] = {
            "coordinator": coordinator,
        }

    else:
        # no configuration information provided
        pass

    return True
