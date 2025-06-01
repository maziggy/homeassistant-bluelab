import logging

import aiohttp
from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN, DEVICE_ATTRIBUTE_URL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Bluelab Guardian switches based on a config entry."""
    devices = hass.data[DOMAIN][entry.entry_id]["devices"]
    api_token = entry.data["api_token"]
    entities = []

    for device in devices:
        for setting in ["settings.alarms", ]:
            entity = BluelabGuardianAlarmSwitch(hass, device, setting, api_token)
            entities.append(entity)

            # Append to attribute_entities
            hass.data[DOMAIN][entry.entry_id]["attribute_entities"].append(entity)

        async_add_entities(entities, update_before_add=True)


class BluelabGuardianAlarmSwitch(SwitchEntity):
    """Representation of the Alarm Enabled switch for Bluelab Guardian."""

    def __init__(self, hass, device, settings, api_token):
        self.hass = hass
        self.device_id = device["id"]
        self._name = f"{device['label']} Alarm Enabled"
        self._settings = settings
        self.api_token = api_token
        self._state = 0  # Represents whether the alarm is enabled
        self._device_name = device["label"]
        self._key = "setting.alarms"  # Set the key for this entity

        _LOGGER.debug("Initializing switch: %s", self._name)

    @property
    def unique_id(self):
        return f"{self.device_id}_alarm_enabled"

    @property
    def is_on(self):
        """Return the current state of the switch."""
        return self._state

    @property
    def name(self):
        return self._name

    @property
    def device_info(self):
        """Return device information for the entity."""
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": self._device_name,
            "manufacturer": "Bluelab",
            "model": "Guardian",
        }

    def update_attributes(self, attributes_data):
        """Update the state of the switch based on attributes."""
        for attribute in attributes_data:
            if attribute["key"] == self._key:
                try:
                    _LOGGER.debug("Updating attributes for %s with data: %s", self._device_name, attributes_data)
                    # Handle plain values or nested dictionaries
                    value = attribute["value"]
                    new_state = value["value"] if isinstance(value, dict) else value
                    if new_state != self._state:
                        _LOGGER.debug("Updating state of %s from %s to %s", self.name, self._state, new_state)
                        self._state = new_state
                        self.async_write_ha_state()
                except (KeyError, TypeError, AttributeError) as e:
                    _LOGGER.error("Failed to update %s: %s", self.name, e)

    async def async_turn_on(self, **kwargs):
        """Turn the alarm on."""
        _LOGGER.debug("Turning on the alarm for %s", self._device_name)
        await self._send_command(True)

    async def async_turn_off(self, **kwargs):
        """Turn the alarm off."""
        _LOGGER.debug("Turning off the alarm for %s", self._device_name)
        await self._send_command(False)

    async def _send_command(self, state):
        self._state = state

        # No need to loop through entities - we're only updating this specific device
        _LOGGER.debug(f"Setting alarm state for device {self.device_id} to {state}")

        # Construct the payload
        payload = {"setting.alarms": self._state, }

        # Debugging
        _LOGGER.debug(f"Constructed payload: {payload}")

        url = f"{DEVICE_ATTRIBUTE_URL}{self.device_id}"
        headers = {
            "Authorization": f"{self.api_token}",
            "Content-Type": "application/json",
        }

        _LOGGER.debug("Sending PUT request to %s with payload: %s", url, payload)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, json=payload, headers=headers) as response:
                    response_text = await response.text()
                    if response.status != 200:
                        raise ValueError(f"Failed to set settings: HTTP {response.status} {response_text}")
                    _LOGGER.debug("Successfully set alarm state for %s to %s", self._device_name, self._state)
                    self._state = state
                    self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to set settings for device %s: %s", self.device_id, e)
