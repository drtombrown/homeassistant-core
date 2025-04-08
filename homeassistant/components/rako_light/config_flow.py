"""Config flow for Rako Light integration."""

import asyncio
from typing import Any

from rakopy.hub import Hub
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import CLIENT_NAME, DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})


async def validate_user_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.

    At this stage the data ha already been validated according to STEP_USER_DATA_SCHEMA (?),
    so all that remains is to determine whether the hostname of the hub is valid.
    """

    hub = Hub(CLIENT_NAME, data[CONF_HOST])
    # pp(hub)

    try:
        # Attempt to connect to the hub and get its status
        # This will raise an exception if the connection fails
        await asyncio.wait_for(hub.get_hub_status(), timeout=5)
    except TimeoutError:
        # pp("no connection to hub")
        raise HomeAssistantError("Could not connect to Rako Hub") from TimeoutError
    else:
        # If the connection was successful, we can proceed (return None)
        # pp("connection successful")
        pass


class RakoLightConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rako Light."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""

        # pp("config flow init")

        # self.data: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Implement config flow that is invoked when a user clicks adds the integration as a new integration from the Home Assistant settings."""

        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate the input using STEP_USER_DATA_SCHEMA
            try:
                await validate_user_input(self.hass, user_input)

                # self.data = user_input

                # configuration is valid
                # proceed to the next step
                # create the config entry
                return self.async_create_entry(
                    title=user_input[CONF_HOST],
                    data=user_input,
                )

            except HomeAssistantError as err:
                errors["base"] = str(err)

                return self.async_show_form(
                    step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
                )

        else:
            # If no user input, show the form
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )
