import logging
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
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

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        if self.sensor_type == "temperature":
            return SensorDeviceClass.TEMPERATURE  # Predefined device class for temperature
        elif self.sensor_type == "electrical_conductivity":
            return SensorDeviceClass.CONDUCTIVITY  # Predefined device class for conductivity
        return None  # No device class for 'ph', so return None

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of the sensor."""
        return ""  # Force a common unit for all sensors

    def update_telemetry(self, telemetry_data):
        """Update sensor state based on telemetry data."""
        _LOGGER.debug("Updating telemetry for %s with data: %s", self.name, telemetry_data)
        if self.sensor_type in telemetry_data:
            try:
                new_state = float(telemetry_data[self.sensor_type][0]["value"])  # Ensure the state is numeric
                if new_state != self._state:
                    _LOGGER.debug("Updating state of %s from %s to %s", self.name, self._state, new_state)
                    self._state = new_state
                    self.async_write_ha_state()
                else:
                    _LOGGER.debug("State of %s remains unchanged at %s", self.name, self._state)
            except (ValueError, TypeError) as e:
                _LOGGER.error("Failed to parse telemetry data for %s: %s", self.name, e)
