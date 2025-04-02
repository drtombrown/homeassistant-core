"""Example integration using DataUpdateCoordinator."""

from dataclasses import dataclass
from datetime import timedelta
import logging

from rakopy.hub import Hub

# from pprint import pp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CLIENT_NAME

_LOGGER = logging.getLogger(__name__)


@dataclass
class RakoLightDataLevel:
    """Data class for Rako Light data level item."""

    channel_id: int
    current_level: int
    target_level: int
    room_id: int


@dataclass
class RakoLightData:
    """Data class for Rako Light data."""

    levels: list[RakoLightDataLevel]

    def find_level(self, channel_id: int, room_id: int) -> RakoLightDataLevel | None:
        """Find a level by channel id and room_id."""

        for level in self.levels:
            if level.channel_id == channel_id and level.room_id == room_id:
                return level
        return None


class RakoLightCoordinator(DataUpdateCoordinator[RakoLightData]):
    """Rako Light Date Update coordinator."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize the coordinator."""

        super().__init__(
            hass,
            logger=_LOGGER,
            # Name - for logging purposes.
            name="Rako Hub",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=60),
            # Set always_update to `False` if the data returned from the
            # api can be compared via `__eq__` to avoid duplicate updates
            # being dispatched to listeners
            always_update=True,
        )

        self._hub = Hub(CLIENT_NAME, host)

    async def _async_setup(self):
        """Set up the coordinator.

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """

        # pp("_async_setup")

    async def _async_update_data(self) -> RakoLightData:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """

        # pp("_async_update_data")

        try:
            hubLevels = await self._hub.get_levels()

            data = RakoLightData(
                levels=[
                    RakoLightDataLevel(
                        channel_id=channel.channel_id,
                        current_level=channel.current_level,
                        target_level=channel.target_level,
                        room_id=room.room_id,
                    )
                    for room in hubLevels
                    for channel in room.channel_levels
                ]
            )

            _LOGGER.info("Fetched (%s) Rako levels", len(data.levels))

            return data  # noqa: TRY300
        except Exception as error:
            raise UpdateFailed(error) from error

    # ----------------------------------------------------------------------------
    # Here we add some custom functions on our data coordinator to be called
    # from entity platforms to get access to the specific data they want.
    #
    # These will be specific to your api or yo may not need them at all
    # ----------------------------------------------------------------------------

    def get_level(self, room_id: int, channel_id: int) -> int:
        """Get the level, given a specific room and channel."""

        level = self.data.find_level(channel_id, room_id)
        if level is None:
            _LOGGER.warning(
                "Could not find level for room_id: %s channel_id: %s",
                room_id,
                channel_id,
            )
            return 0

        return level.current_level

    async def turn_light_on(self, room_id: int, channel_id: int) -> None:
        """Turn on a light."""
        await self._hub.set_level(room_id, channel_id, 255)
        # update level to 255 in data class?

    async def turn_light_off(self, room_id: int, channel_id: int) -> None:
        """Turn off a light."""
        await self._hub.set_level(room_id, channel_id, 0)
        # update level to 0 in data class?

    async def set_light_level(self, room_id: int, channel_id: int, level: int) -> None:
        """Set the light level."""

        await self._hub.set_level(room_id, channel_id, level)
        # update level in data class?
