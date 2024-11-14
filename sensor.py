import logging
from homeassistant.helpers.entity import Entity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Bluelab Guardian sensors based on a config entry."""
    devices = hass.data[DOMAIN][entry.entry_id]["devices"]
    api_token = entry.data["api_token"]

    entities = []
    for device in devices:
        for sensor_type in ["ph", "temperature", "electrical_conductivity"]:
            entity = BluelabGuardianSensor(hass, device, sensor_type, api_token)
            entities.append(entity)

    hass.data[DOMAIN][entry.entry_id]["telemetry_entities"] = entities
    async_add_entities(entities, update_before_add=True)

class BluelabGuardianSensor(Entity):
    """Representation of a Bluelab Guardian sensor."""

    def __init__(self, hass, device, sensor_type, api_token):
        self.hass = hass
        self.device_id = device["id"]
        self._name = f"{device['label']} {sensor_type.capitalize()}"
        self.sensor_type = sensor_type
        self.api_token = api_token
        self._state = None
        self._device_name = device["label"]

    @property
    def unique_id(self):
        return f"{self.device_id}_{self.sensor_type}"

    @property
    def state(self):
        return self._state

    @property
    def name(self):
        return self._name

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": self._device_name,
            "manufacturer": "Bluelab",
            "model": "Guardian",
        }

    @property
    def icon(self):
        """Return the icon for the sensor based on its type."""
        if self.sensor_type == "ph":
            return "mdi:ph"
        elif self.sensor_type == "temperature":
            return "mdi:thermometer"
        elif self.sensor_type == "electrical_conductivity":
            return "mdi:fence-electric"
        return "mdi:eye"  # Default icon

    def update_telemetry(self, telemetry_data):
        """Update sensor state based on telemetry data."""
        if self.sensor_type in telemetry_data:
            new_state = telemetry_data[self.sensor_type][0]["value"]
            _LOGGER.debug("Fetched telemetry for %s: %s", self.sensor_type, new_state)
            
            # Check if the new state is different from the current state
            if new_state != self._state:
                _LOGGER.debug("Updating state of %s from %s to %s", self._name, self._state, new_state)
                self._state = new_state
                self.async_write_ha_state()
            else:
                _LOGGER.debug("State of %s remains unchanged at %s", self._name, self._state)
