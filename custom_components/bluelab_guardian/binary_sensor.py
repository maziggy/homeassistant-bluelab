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
        for alarm_type in [
            "ph_high_alarm",
            "ph_low_alarm",
            "temp_high_alarm",
            "temp_low_alarm",
            "ec_high_alarm",
            "ec_low_alarm",
            "calibration_required",
        ]:
            entity = BluelabGuardianAlarmBinarySensor(hass, device, alarm_type, api_token)
            entities.append(entity)

        # REMOVE ALARM ENABLED FROM HERE
        # Previously, a binary sensor was created for "alarm_enabled", but we no longer want this.

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
        if self.alarm_type == "calibration_required":
            return "mdi:alert-circle-check"
        elif "low_alarm" in self.alarm_type:
            return "mdi:alert"
        elif "high_alarm" in self.alarm_type:
            return "mdi:alert-circle"
        return "mdi:eye"

    def update_attributes(self, attributes_data):
        """Update binary sensor state based on device attributes."""
        for attribute in attributes_data:
            if attribute["key"] == f"alarm.{self.alarm_type}":
                new_state = attribute["value"]
                if new_state != self._state:
                    _LOGGER.debug("Updating state of %s from %s to %s", self.name, self._state, new_state)
                    self._state = new_state
                    self.async_write_ha_state()
                else:
                    _LOGGER.debug("State of %s remains unchanged at %s", self.name, self._state)


class BluelabGuardianAlarmSettingBinarySensor(BinarySensorEntity):
    """Representation of the Bluelab Guardian alarm setting (on/off)."""

    def __init__(self, hass, device, api_token):
        """Initialize the entity."""
        self.hass = hass
        self.device_id = device["id"]
        self._name = f"{device['label']} Alarm Enabled"
        self.api_token = api_token
        self._state = None
        self._device_name = device["label"]

    @property
    def unique_id(self):
        return f"{self.device_id}_setting_alarms"

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
        """Icon to represent the state."""
        return "mdi:bell-ring" if self._state else "mdi:bell-off"

    def update_attributes(self, attributes_data):
        """Update the state based on the fetched attributes."""
        for attribute in attributes_data:
            if attribute["key"] == "setting.alarms":
                new_state = attribute["value"]
                if new_state != self._state:
                    _LOGGER.debug("Updating %s state from %s to %s", self.name, self._state, new_state)
                    self._state = new_state
                    self.async_write_ha_state()
