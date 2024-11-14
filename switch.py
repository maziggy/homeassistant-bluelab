import logging
import requests
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    devices = hass.data[DOMAIN][entry.entry_id]["devices"]
    entities = [BluelabGuardianSwitch(hass, device, entry.data["api_token"]) for device in devices]
    async_add_entities(entities, update_before_add=True)

class BluelabGuardianSwitch(SwitchEntity):
    def __init__(self, hass, device, api_token):
        self.hass = hass
        self.device_id = device["id"]
        self._name = f"{device['label']} Alarms"
        self.api_token = api_token
        self._state = False

    @property
    def unique_id(self):
        return f"{self.device_id}_alarms"

    async def async_turn_on(self):
        await self._set_state(True)

    async def async_turn_off(self):
        await self._set_state(False)

    async def _set_state(self, state):
        attributes_url = f"https://api.edenic.io/api/v1/device-attribute/{self.device_id}"
        headers = {"Authorization": self.api_token}
        response = await self.hass.async_add_executor_job(lambda: requests.post(
            attributes_url, json={"key": "setting.alarms", "value": state}, headers=headers))
        response.raise_for_status()
        self._state = state
        self.async_write_ha_state()
