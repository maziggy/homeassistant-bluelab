import os
import shutil
import logging
import requests
import asyncio
import aiofiles
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN, DEVICE_LIST_URL, TELEMETRY_URL, DEVICE_ATTRIBUTE_URL, CONF_API_TOKEN, TELEMETRY_UPDATE_INTERVAL, ATTRIBUTE_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bluelab Guardian from a config entry."""

    # Copy static files asynchronously
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

    # Forward entry setup to sensor and binary_sensor platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])

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

    # Forward entry setup to sensor and binary_sensor platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])

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
            _LOGGER.debug("Telemetry data for device %s: %s", device_id, telemetry_data)

            for entity in hass.data[DOMAIN][entry.entry_id].get("telemetry_entities", []):
                if entity.device_id == device_id:
                    entity.update_telemetry(telemetry_data)

        except requests.RequestException as err:
            _LOGGER.error("Failed to fetch telemetry for device %s: %s", device_id, err)


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

            for entity in hass.data[DOMAIN][entry.entry_id].get("attribute_entities", []):
                if entity.device_id == device_id:
                    entity.update_attributes(attributes_data)

        except requests.RequestException as err:
            _LOGGER.error("Failed to fetch attributes for device %s: %s", device_id, err)
