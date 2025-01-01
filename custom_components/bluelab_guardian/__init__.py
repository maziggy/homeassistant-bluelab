import logging
import time
import os

import aiofiles
import requests
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, DEVICE_LIST_URL, TELEMETRY_URL, DEVICE_ATTRIBUTE_URL, CONF_API_TOKEN, \
    TELEMETRY_UPDATE_INTERVAL, ATTRIBUTE_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def copy_static_files(hass: HomeAssistant):
    """Copy static assets to the www directory."""
    src_dir = os.path.join(os.path.dirname(__file__))
    dst_dir = os.path.join(hass.config.path("www"), "custom_components", "bluelab_guardian")

    _LOGGER.debug("Source directory: %s", src_dir)
    _LOGGER.debug("Destination directory: %s", dst_dir)

    # Ensure the destination directory exists
    os.makedirs(dst_dir, exist_ok=True)

    # Copy the icon and logo files
    for file_name in ["icon.png", "logo.png"]:
        src_file = os.path.join(src_dir, file_name)
        dst_file = os.path.join(dst_dir, file_name)

        _LOGGER.debug("Copying %s to %s", src_file, dst_file)

        if os.path.exists(src_file):
            async with aiofiles.open(src_file, "rb") as src:
                async with aiofiles.open(dst_file, "wb") as dst:
                    while chunk := await src.read(1024 * 1024):  # Read in chunks
                        await dst.write(chunk)
        else:
            _LOGGER.error("File %s does not exist", src_file)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bluelab Guardian from a config entry."""

    # Copy static files on setup
    await copy_static_files(hass)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    api_token = entry.data[CONF_API_TOKEN]
    organization_id = entry.data.get("organization_id")
    headers = {"Authorization": api_token}

    device_list_url = f"{DEVICE_LIST_URL}{organization_id}"
    try:
        response = await hass.async_add_executor_job(lambda: requests.get(device_list_url, headers=headers))
        response.raise_for_status()
        devices = response.json()
        _LOGGER.info("Devices fetched: %s", devices)
        hass.data[DOMAIN][entry.entry_id]["devices"] = devices
    except requests.RequestException as err:
        _LOGGER.error("Failed to fetch devices: %s", err)
        return False

    # Track entities for telemetry and attributes
    hass.data[DOMAIN][entry.entry_id]["telemetry_entities"] = []  # For sensor entities
    hass.data[DOMAIN][entry.entry_id]["attribute_entities"] = []  # For number entities

    # Forward entry setup to sensor, binary_sensor, and number platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor", "number", "switch"])

    # Trigger initial telemetry and attribute updates
    await async_update_telemetry(hass, entry)  # Immediate telemetry update
    await async_update_device_attributes(hass, entry)  # Immediate attributes update

    # Schedule telemetry and attribute updates with event-loop-safe scheduling
    async def schedule_telemetry_update(now):
        await async_update_telemetry(hass, entry)

    async def schedule_attribute_update(now):
        await async_update_device_attributes(hass, entry)

    # Use event-loop-safe scheduling
    async_track_time_interval(hass, schedule_telemetry_update, TELEMETRY_UPDATE_INTERVAL)
    async_track_time_interval(hass, schedule_attribute_update, ATTRIBUTE_UPDATE_INTERVAL)

    return True


async def async_update_telemetry(hass: HomeAssistant, entry: ConfigEntry):
    """Fetch and update telemetry data for all devices."""
    _LOGGER.debug("Starting telemetry update...")
    api_token = entry.data[CONF_API_TOKEN]
    headers = {"Authorization": api_token}
    devices = hass.data[DOMAIN][entry.entry_id].get("devices", [])

    for device in devices:
        device_id = device["id"]
        telemetry_url = f"{TELEMETRY_URL}{device_id}"

        try:
            response = await hass.async_add_executor_job(lambda: requests.get(telemetry_url, headers=headers))
            response.raise_for_status()
            telemetry_data = response.json()
            # Apply telemetry updates to all sensor entities
            for entity in hass.data[DOMAIN][entry.entry_id]["telemetry_entities"]:
                if entity.device_id == device_id:
                    entity.update_telemetry(telemetry_data)
        except requests.RequestException as err:
            _LOGGER.info("Failed to fetch telemetry for device %s: %s", device_id, err)


async def async_update_device_attributes(hass: HomeAssistant, entry: ConfigEntry):
    """Fetch and update device attributes for all devices."""
    _LOGGER.debug("Starting device attribute update...")
    api_token = entry.data[CONF_API_TOKEN]
    headers = {"Authorization": api_token}
    devices = hass.data[DOMAIN][entry.entry_id].get("devices", [])

    for device in devices:
        device_id = device["id"]
        attributes_url = f"{DEVICE_ATTRIBUTE_URL}{device_id}"

        try:
            response = await hass.async_add_executor_job(lambda: requests.get(attributes_url, headers=headers))
            response.raise_for_status()
            attributes_data = response.json()
            _LOGGER.debug("Attributes data for device %s: %s", device_id, attributes_data)

            # Apply attribute updates to all entities
            for entity in hass.data[DOMAIN][entry.entry_id]["attribute_entities"]:
                if entity.device_id == device_id:
                    _LOGGER.debug(f"device_id: {device_id}")
                    entity.update_attributes(attributes_data)
        except requests.RequestException as err:
            _LOGGER.info("Failed to fetch attributes for device %s: %s", device_id, err)
