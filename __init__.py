import logging
import requests
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN, TELEMETRY_URL, DEVICE_ATTRIBUTE_URL, CONF_API_TOKEN

_LOGGER = logging.getLogger(__name__)
TELEMETRY_UPDATE_INTERVAL = timedelta(seconds=70)
ATTRIBUTE_UPDATE_INTERVAL = timedelta(minutes=5)

async def async_test_task(hass):
    """Simple test task to verify async_track_time_interval."""
    print("async_test_task: Scheduler is working")

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bluelab Guardian from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    api_token = entry.data[CONF_API_TOKEN]
    organization_id = entry.data.get("organization_id")
    headers = {"Authorization": api_token}

    device_list_url = f"https://api.edenic.io/api/v1/device/{organization_id}"
    try:
        response = await hass.async_add_executor_job(lambda: requests.get(device_list_url, headers=headers))
        response.raise_for_status()
        devices = response.json()
        _LOGGER.info("Devices fetched: %s", devices)
        hass.data[DOMAIN][entry.entry_id]["devices"] = devices
    except requests.RequestException as err:
        _LOGGER.error("Failed to fetch devices: %s", err)
        return False

    # Forward entry setup to sensor and binary_sensor platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])

    # Directly test telemetry and attribute updates
    await async_update_telemetry(hass, entry)
    await async_update_device_attributes(hass, entry)

    # Schedule telemetry and device attribute updates with proper async handling
    async_track_time_interval(hass, lambda now: hass.async_create_task(async_update_telemetry(hass, entry)), TELEMETRY_UPDATE_INTERVAL)
    async_track_time_interval(hass, lambda now: hass.async_create_task(async_update_device_attributes(hass, entry)), ATTRIBUTE_UPDATE_INTERVAL)
    
    # Schedule test task
    async_track_time_interval(hass, lambda now: hass.async_create_task(async_test_task(hass)), timedelta(seconds=30))

    return True

async def async_update_telemetry(hass: HomeAssistant, entry: ConfigEntry):
    """Fetch and update telemetry data for all devices."""
    print("async_update_telemetry called")
    api_token = entry.data[CONF_API_TOKEN]
    headers = {"Authorization": api_token}
    devices = hass.data[DOMAIN][entry.entry_id].get("devices", [])

    for device in devices:
        device_id = device["id"]
        telemetry_url = f"https://api.edenic.io/api/v1/telemetry/{device_id}"
        
        try:
            response = await hass.async_add_executor_job(lambda: requests.get(telemetry_url, headers=headers))
            response.raise_for_status()
            telemetry_data = response.json()
            print("Telemetry data for device:", telemetry_data)
            _LOGGER.debug("Telemetry data for device %s: %s", device_id, telemetry_data)

            for entity in hass.data[DOMAIN][entry.entry_id]["telemetry_entities"]:
                if entity.device_id == device_id:
                    entity.update_telemetry(telemetry_data)

        except requests.RequestException as err:
            _LOGGER.error("Failed to fetch telemetry for device %s: %s", device_id, err)

async def async_update_device_attributes(hass: HomeAssistant, entry: ConfigEntry):
    """Fetch and update device attributes for all devices."""
    print("async_update_device_attributes called")
    api_token = entry.data[CONF_API_TOKEN]
    headers = {"Authorization": api_token}
    devices = hass.data[DOMAIN][entry.entry_id].get("devices", [])

    for device in devices:
        device_id = device["id"]
        attributes_url = f"https://api.edenic.io/api/v1/device-attribute/{device_id}"

        try:
            response = await hass.async_add_executor_job(lambda: requests.get(attributes_url, headers=headers))
            response.raise_for_status()
            attributes_data = response.json()
            print("Attributes data for device:", attributes_data)
            _LOGGER.debug("Attributes data for device %s: %s", device_id, attributes_data)

            for entity in hass.data[DOMAIN][entry.entry_id]["attribute_entities"]:
                if entity.device_id == device_id:
                    entity.update_attributes(attributes_data)

        except requests.RequestException as err:
            _LOGGER.error("Failed to fetch attributes for device %s: %s", device_id, err)
