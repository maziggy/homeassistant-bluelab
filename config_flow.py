import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_TOKEN
from .const import DOMAIN, CONF_ORGANIZATION_ID

class BluelabGuardianConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bluelab Guardian integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Save both api_token and organization_id
            return self.async_create_entry(title="Bluelab Guardian", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ORGANIZATION_ID): str,
                vol.Required(CONF_API_TOKEN): str
            })
        )
