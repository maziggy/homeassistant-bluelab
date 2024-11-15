import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Bluelab Guardian binary sensors based on a config entry."""
    devices = hass.data[DOMAIN][entry.entry_id]["devices"]
    api_token = entry.data["api_token"]

    entities = []
    for device in devices:
        for alarm_type in ["ph_high_alarm", "ph_low_alarm", "temp_high_alarm", "temp_low_alarm", "ec_high_alarm", "ec_low_alarm"]:
            entity = BluelabGuardianAlarmBinarySensor(hass, device, alarm_type, api_token)
            entities.append(entity)

    hass.data[DOMAIN][entry.entry_id]["attribute_entities"] = entities
    async_add_entities(entities, update_before_add=True)

class BluelabGuardianAlarmBinarySensor(BinarySensorEntity):
    """Representation of a Bluelab Guardian binary sensor for alarms."""

    def __init__(self, hass, device, alarm_type, api_token):
        self.hass = hass
        self.device_id = device["id"]
        self._name = f"{device['label']} {alarm_type.replace('_', ' ').capitalize()}"
        self.alarm_type = alarm_type
        self.api_token = api_token
        self._state = None
        self._device_name = device["label"]

    @property
    def unique_id(self):
        return f"{self.device_id}_{self.alarm_type}"

    @property
    def is_on(self):
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
        """Return an icon specific to the alarm type."""
        if "binary_sensor.water_monitor_ec_high_alarm" in self.alarm_type:
            return "mdi:alert-circle"
        elif "low_alarm" in self.alarm_type:
            return "mdi:alert"
        return "mdi:eye"  # Default alarm icon
        
    def update_attributes(self, attributes_data):
        """Update binary sensor state based on device attributes."""
        for attribute in attributes_data:
            if attribute["key"] == f"alarm.{self.alarm_type}":
                new_state = attribute["value"]
                _LOGGER.debug("Fetched attribute for %s: %s", self.alarm_type, new_state)
                
                if new_state != self._state:
                    _LOGGER.debug("Updating state of %s from %s to %s", self._name, self._state, new_state)
                    self._state = new_state
                    self.async_write_ha_state()
                else:
                    _LOGGER.debug("State of %s remains unchanged at %s", self._name, self._state)
