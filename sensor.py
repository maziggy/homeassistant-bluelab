import logging
from homeassistant.helpers.entity import Entity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    devices = hass.data[DOMAIN][entry.entry_id]["devices"]
    entities = []
    for device in devices:
        for sensor_type in ["ph", "temperature", "electrical_conductivity"]:
            entity = BluelabGuardianSensor(hass, device, sensor_type, entry.data["api_token"])
            entities.append(entity)
    async_add_entities(entities, update_before_add=True)

class BluelabGuardianSensor(Entity):
    def __init__(self, hass, device, sensor_type, api_token):
        self.hass = hass
        self.device_id = device["id"]
        self._name = f"{device['label']} {sensor_type.capitalize()}"
        self.sensor_type = sensor_type
        self.api_token = api_token
        self._state = None

    @property
    def unique_id(self):
        return f"{self.device_id}_{self.sensor_type}"

    @property
    def state(self):
        return self._state

    def update_telemetry(self, telemetry_data):
        if self.sensor_type in telemetry_data:
            self._state = telemetry_data[self.sensor_type][0]["value"]
            self.async_write_ha_state()
