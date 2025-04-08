"""Example integration using DataUpdateCoordinator."""

from dataclasses import dataclass
from datetime import timedelta
import logging

# from pprint import pp
from rakopy.hub import Hub
from rakopy.model import HubStatus

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
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
    """Data class for Rako Light."""

    room_id: int
    channel_id: int
    name: str
    room_name: str
    type: str


@dataclass
class RakoHubLightLevelsData:
    """Data class for Rako Light data."""

    levels: list[RakoLightDataLevel]

    def find_level(self, channel_id: int, room_id: int) -> RakoLightDataLevel | None:
        """Find a level by channel id and room_id."""

        for level in self.levels:
            # pp(
            #     f"find_level: {room_id=}, {channel_id=}, {level.room_id=}, {level.channel_id=}"
            # )
            if level.channel_id == channel_id and level.room_id == room_id:
                return level

        return None


type RakoLightConfigEntry = ConfigEntry[RakoLightCoordinator]


class RakoLightCoordinator(DataUpdateCoordinator[RakoHubLightLevelsData]):
    """Rako Light Date Update coordinator."""

    config_entry: RakoLightConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: RakoLightConfigEntry) -> None:
        """Initialize the coordinator."""

        super().__init__(
            hass,
            logger=_LOGGER,
            # Name - for logging purposes.
            name="Rako Hub",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=10),
            # Set always_update to `False` if the data returned from the
            # api can be compared via `__eq__` to avoid duplicate updates
            # being dispatched to listeners
            always_update=True,
        )

        self._hub = Hub(CLIENT_NAME, config_entry.data[CONF_HOST])

    async def _async_setup(self):
        """Set up the coordinator.

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """

        # pp("_async_setup")

    async def discover_lights(self) -> list[RakoLightData]:
        """Discover lights associated with Rako Hub."""

        rako_rooms = await self._hub.get_rooms()
        return [
            RakoLightData(
                room_id=room.id,
                channel_id=channel.id,
                name=channel.title,
                room_name=room.title,
                type=channel.type,
            )
            for room in rako_rooms
            for channel in room.channels
        ]

    async def _async_update_data(self) -> RakoHubLightLevelsData:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """

        # pp("_async_update_data")

        try:
            hubLevels = await self._hub.get_levels()

            data = RakoHubLightLevelsData(
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

    async def get_hub_status(self) -> HubStatus:
        """Get hub info."""

        return await self._hub.get_hub_status()

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

    async def set_light_level(
        self, room_id: int, channel_id: int, brightness: int
    ) -> None:
        """Set the light brightness (level)."""

        await self._hub.set_level(room_id, channel_id, brightness)
        # update level in data class?

        await self.async_request_refresh()
