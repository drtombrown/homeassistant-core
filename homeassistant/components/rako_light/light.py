"""Platform for light integration."""

from __future__ import annotations

import logging
from pprint import pp
from typing import Any

from homeassistant.components.light import (
    # PLATFORM_SCHEMA as LIGHT_PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import RakoLightCoordinator, RakoLightData

_LOGGER = logging.getLogger(__name__)


# async def async_setup_platform(
#     hass: HomeAssistant,
#     config: ConfigType,
#     add_entities: AddEntitiesCallback,
#     _discovery_info: DiscoveryInfoType | None = None,
# ) -> None:
#     """Set up the Rako Light platform."""

#     coordinator = hass.data[DOMAIN]["coordinator"]

#     add_entities([RakoLight(coordinator, config)])


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[RakoLightCoordinator],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Rako Light platform from a config entry."""

    pp("Rako Light :: async_setup_entry")

    coordinator = config_entry.runtime_data
    # pp(coordinator)

    rako_hub_lights = await coordinator.discover_lights()
    # pp(rako_hub_lights)

    entities_to_add = [
        RakoLight(coordinator=coordinator, light_data=rako_hub_light)
        for rako_hub_light in rako_hub_lights
    ]

    async_add_entities(entities_to_add)


class RakoLight(CoordinatorEntity[RakoLightCoordinator], LightEntity):
    """Representation of an Rako Light."""

    def __init__(
        self, coordinator: RakoLightCoordinator, light_data: RakoLightData
    ) -> None:
        """Initialize a RakoLight."""

        self._unique_id = f"rako_light__room_id:{light_data.room_id}_channel_id:{light_data.channel_id}"

        super().__init__(coordinator, context=self._unique_id)

        # pp("light.py __init__")
        # pp(light_data)

        self._name = light_data.name
        self._room_id = light_data.room_id
        self._channel_id = light_data.channel_id
        self._color_mode = (
            ColorMode.BRIGHTNESS if light_data.type == "SLIDER" else ColorMode.ONOFF
        )

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

    @property
    def unique_id(self):
        """Return a unique ID for this light."""

        return self._unique_id

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """

        brightness = kwargs.get("brightness", 255)

        pp(
            f"RakoLight::async_turn_on: {self._room_id=}, {self._channel_id=}, {brightness=}"
        )

        await self.coordinator.set_light_level(
            self._room_id, self._channel_id, brightness
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""

        pp(f"RakoLight::async_turn_on: {self._room_id=}, {self._channel_id=}")

        await self.coordinator.set_light_level(self._room_id, self._channel_id, 0)

    @property
    def color_mode(self) -> ColorMode | str | None:
        """Return the current color mode."""
        return self._color_mode

    @property
    def supported_color_modes(self) -> set[ColorMode] | set[str] | None:
        """Declare which color modes this light supports."""
        return {self._color_mode}

    @property
    def should_poll(self) -> bool:
        """Fetch data via coordinator."""
        return False
