import logging

import aiohttp
from homeassistant.components.number import NumberEntity

from .const import DOMAIN, DEVICE_ATTRIBUTE_URL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Bluelab Guardian number entities based on a config entry."""
    devices = hass.data[DOMAIN][entry.entry_id]["devices"]
    api_token = entry.data["api_token"]

    entities = []
    for device in devices:
        for setting in [
            "ph_low_alarm",
            "ph_high_alarm",
            "ec_low_alarm",
            "ec_high_alarm",
            "temp_low_alarm",
            "temp_high_alarm",
        ]:
            entity = BluelabGuardianNumber(hass, device, setting, api_token)
            entities.append(entity)

            # Append to attribute_entities
            hass.data[DOMAIN][entry.entry_id]["attribute_entities"].append(entity)

    async_add_entities(entities, update_before_add=True)


class BluelabGuardianNumber(NumberEntity):
    """Representation of a Bluelab Guardian numeric setting."""

    def __init__(self, hass, device, setting, api_token):
        """Initialize the number entity."""
        self.hass = hass
        self._state = 0
        self.device_id = device["id"]
        self.setting = setting
        self.api_token = api_token
        self._device_name = device["label"]

    @property
    def unique_id(self):
        """Return a unique ID for the entity."""
        return f"{self.device_id}_{self.setting}"

    @property
    def name(self):
        """Return the display name of the entity."""
        return f"{self._device_name} {self.setting.replace('_', ' ').capitalize()}"

    @property
    def native_value(self):
        """Return the current value of the threshold."""
        return self._state

    @property
    def native_min_value(self):
        """Return the minimum value for the threshold."""
        return 0  # Adjust as per device specifications

    @property
    def native_max_value(self):
        """Return the maximum value for the threshold."""
        return 100  # Adjust as per device specifications

    @property
    def native_step(self):
        """Return the step value for adjustments."""
        return 0.1  # Adjust as per device specifications

    @property
    def device_info(self):
        """Return device information for the entity."""
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": self._device_name,
            "manufacturer": "Bluelab",
            "model": "Guardian",
        }

    async def async_set_native_value(self, value):
        """Set a new threshold value."""
        _LOGGER.debug("Setting %s to %s", self.name, value)

        # Save the new value locally
        self._state = value
        self.async_write_ha_state()

        await self._send_command(self._state)

        # TODO: Add API logic to update the threshold on the device
        # Example API call:
        # url = f"{YOUR_API_ENDPOINT}/{self.device_id}/thresholds"
        # payload = {"setting": self.setting, "value": value}
        # headers = {"Authorization": f"Bearer {self.api_token}"}
        # await self.hass.async_add_executor_job(requests.post, url, json=payload, headers=headers)

    def update_attributes(self, attributes_data):
        """Update the state of the numeric threshold based on attributes."""
        for attribute in attributes_data:
            if attribute["key"] == f"setting.{self.setting}":  # Match the specific setting key
                try:
                    _LOGGER.debug(f"attribute: {attribute}")

                    # Extract the nested "value" field
                    new_state = float(attribute["value"]["value"])  # Ensure numeric value
                    if new_state != self._state:
                        _LOGGER.debug("Updating state of %s from %s to %s", self.name, self._state, new_state)
                        self._state = new_state
                        self.async_write_ha_state()
                except (ValueError, TypeError, KeyError) as e:
                    # _LOGGER.error("Error updating %s: %s", self.name, e)
                    _LOGGER.debug(f"Error updating: name: {self.name}, state: {self._state}, new_state: {new_state}")

    async def _send_command(self, state):
        # Access the top-level domain data dynamically
        domain_data = self.hass.data.get(DOMAIN, {})
        if not domain_data:
            _LOGGER.error("No data found under DOMAIN.")
            return

        _LOGGER.debug(f"domain_data: {domain_data}")

        # Get the first key dynamically and attribute entities
        first_key = next(iter(domain_data))
        attribute_entities = domain_data[first_key].get('attribute_entities', [])

        _LOGGER.debug(f"attribute_entities: {attribute_entities}")

        # Extract relevant values from attribute_entities
        alarms = {
            "ph_low_alarm": 0.0,
            "ph_high_alarm": 0.0,
            "ec_low_alarm": 0.0,
            "ec_high_alarm": 0.0,
            "temp_low_alarm": 0,
            "temp_high_alarm": 0,
        }

        for entity in attribute_entities:
            entity_str = entity.entity_id
            if "number.water_monitor_ph_low_alarm" in entity_str:
                alarms["ph_low_alarm"] = float(self.hass.states.get(entity_str).state) or 0.0
            elif "number.water_monitor_ph_high_alarm" in entity_str:
                alarms["ph_high_alarm"] = float(self.hass.states.get(entity_str).state) or 0.0
            elif "number.water_monitor_ec_low_alarm" in entity_str:
                alarms["ec_low_alarm"] = float(self.hass.states.get(entity_str).state) or 0.0
            elif "number.water_monitor_ec_high_alarm" in entity_str:
                alarms["ec_high_alarm"] = float(self.hass.states.get(entity_str).state) or 0.0
            elif "number.water_monitor_temp_low_alarm" in entity_str:
                alarms["temp_low_alarm"] = int(float(self.hass.states.get(entity_str).state)) or 0
            elif "number.water_monitor_temp_high_alarm" in entity_str:
                alarms["temp_high_alarm"] = int(float(self.hass.states.get(entity_str).state)) or 0

        # Construct the payload
        payload = {
            "setting.ph_low_alarm": round(alarms["ph_low_alarm"], 2),
            "setting.ph_high_alarm": round(alarms["ph_high_alarm"], 2),
            "setting.ec_low_alarm": round(alarms["ec_low_alarm"], 2),
            "setting.ec_high_alarm": round(alarms["ec_high_alarm"], 2),
            "setting.temp_low_alarm": alarms["temp_low_alarm"],
            "setting.temp_high_alarm": alarms["temp_high_alarm"],
            "setting.alarms": True,  # Ensure 'state' is defined or replace with a valid boolean
        }

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
                        raise ValueError(f"Failed to set alarms: HTTP {response.status} {response_text}")
                    _LOGGER.debug("Successfully set alarm state for %s to %s", self._device_name, state)
                    self._state = state
                    self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to set alarms for device %s: %s", self.device_id, e)
