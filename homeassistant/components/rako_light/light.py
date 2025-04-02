"""Platform for light integration."""

from __future__ import annotations

import logging
from typing import Any

# from pprint import pp
import voluptuous as vol

from homeassistant.components.light import (
    PLATFORM_SCHEMA as LIGHT_PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_CHANNEL_ID, CONF_ROOM_ID, CONF_SUPPORTED_COLOR_MODES, DOMAIN
from .coordinator import RakoLightCoordinator

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = LIGHT_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ROOM_ID): cv.positive_int,
        vol.Required(CONF_CHANNEL_ID): cv.positive_int,
        vol.Required(CONF_SUPPORTED_COLOR_MODES): vol.All(
            cv.ensure_list, [vol.In(ColorMode)]
        ),
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    _discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Rako Light platform."""

    coordinator = hass.data[DOMAIN]["coordinator"]

    add_entities([RakoLight(coordinator, config)])


class RakoLight(CoordinatorEntity[RakoLightCoordinator], LightEntity):
    """Representation of an Rako Light."""

    def __init__(self, coordinator: RakoLightCoordinator, config: ConfigType) -> None:
        """Initialize a RakoLight."""

        super().__init__(coordinator)

        self._name = config[CONF_NAME]
        self._room_id = config[CONF_ROOM_ID]
        self._channel_id = config[CONF_CHANNEL_ID]
        self._supported_color_modes = config[CONF_SUPPORTED_COLOR_MODES]

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """

        return self.coordinator.get_level(self._room_id, self._channel_id)

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""

        return self.coordinator.get_level(self._room_id, self._channel_id) > 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """

        await self.coordinator.turn_light_on(self._room_id, self._channel_id)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""

        await self.coordinator.turn_light_off(self._room_id, self._channel_id)

    @property
    def supported_color_modes(self) -> set[ColorMode] | set[str] | None:
        """Declare which color modes this light supports."""
        return self._supported_color_modes

    @property
    def color_mode(self) -> ColorMode | str | None:
        """Return the current color mode."""
        return self._supported_color_modes[0]
