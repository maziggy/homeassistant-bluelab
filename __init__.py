import logging
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN, TELEMETRY_UPDATE_INTERVAL, TELEMETRY_URL, DEVICE_ATTRIBUTE_URL

_LOGGER = logging.getLogger(__name__)

async def async_update_telemetry(hass, entry):
    """Fetch telemetry data and attributes from the API and update entities."""
    devices = hass.data[DOMAIN][entry.entry_id]["devices"]
    api_token = entry.data["api_token"]
    headers = {"Authorization": api_token}

    telemetry_data = {}
    attributes_data = []

    for device in devices:
        device_id = device["id"]
        
        telemetry_response = await hass.async_add_executor_job(
            lambda: requests.get(f"{TELEMETRY_URL}{device_id}", headers=headers)
        )
        attributes_response = await hass.async_add_executor_job(
            lambda: requests.get(f"{DEVICE_ATTRIBUTE_URL}{device_id}", headers=headers)
        )

        if telemetry_response.status_code == 200:
            telemetry_data[device_id] = telemetry_response.json()
        else:
            _LOGGER.error("Failed to fetch telemetry for device %s", device_id)

        if attributes_response.status_code == 200:
            attributes_data.extend(attributes_response.json())
        else:
            _LOGGER.error("Failed to fetch attributes for device %s", device_id)

    # Update sensors with telemetry data
    for entity in hass.data[DOMAIN][entry.entry_id].get("telemetry_entities", []):
        entity.update_telemetry(telemetry_data.get(entity.device_id, {}))

    # Update sensors and switches with attributes data
    for entity in hass.data[DOMAIN][entry.entry_id].get("attribute_entities", []):
        entity.update_attributes(attributes_data)

async def async_setup_entry(hass, entry):
    """Set up Bluelab Guardian from a config entry."""
    api_token = entry.data["api_token"]
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api_token": api_token,
        "devices": await fetch_devices(api_token),
    }
    async_track_time_interval(
        hass, lambda now: hass.async_create_task(async_update_telemetry(hass, entry)), TELEMETRY_UPDATE_INTERVAL
    )
    return True

async def fetch_devices(api_token):
    headers = {"Authorization": api_token}
    response = await hass.async_add_executor_job(lambda: requests.get(DEVICE_LIST_URL, headers=headers))
    return response.json() if response.status_code == 200 else []
