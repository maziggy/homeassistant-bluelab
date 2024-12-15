import logging
from homeassistant.components.sensor import SensorEntity
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

            # Append to telemetry_entities
            hass.data[DOMAIN][entry.entry_id]["telemetry_entities"].append(entity)

    async_add_entities(entities, update_before_add=True)


class BluelabGuardianSensor(SensorEntity):
    """Representation of a Bluelab Guardian telemetry sensor."""

    def __init__(self, hass, device, sensor_type, api_token):
        self.hass = hass
        self.device_id = device["id"]
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
        return f"{self._device_name} {self.sensor_type.capitalize()}"

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
        """Return the icon for the sensor."""
        if self.sensor_type == "ph":
            return "mdi:ph"
        elif self.sensor_type == "temperature":
            return "mdi:thermometer"
        elif self.sensor_type == "electrical_conductivity":
            return "mdi:fence-electric"
        return "mdi:eye"

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        if self.sensor_type == "temperature":
            return SensorDeviceClass.TEMPERATURE
        elif self.sensor_type == "electrical_conductivity":
            return SensorDeviceClass.CONDUCTIVITY
        return None

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    def update_telemetry(self, telemetry_data):
        """Update sensor state based on telemetry data."""
        if self.sensor_type in telemetry_data:
            try:
                # Extract the first "value" from telemetry_data for this sensor type
                new_state = float(telemetry_data[self.sensor_type][0]["value"])  # Ensure numeric value
                if new_state != self._state:
                    _LOGGER.debug("Updating state of %s from %s to %s", self.name, self._state, new_state)
                    self._state = new_state
                    self.async_write_ha_state()
            except (ValueError, TypeError, KeyError) as e:
                _LOGGER.error("Error updating telemetry for %s: %s", self.name, e)

    def update_attributes(self, attributes_data):
        """Update attributes dynamically."""
        # Example of processing attributes if needed
        for attribute in attributes_data:
            if attribute["key"] == f"{self.sensor_type}":
                self._state = attribute["value"]
                self.async_write_ha_state()