#!/usr/bin/env python3

import aiohttp
import asyncio

DEVICE_LIST_URL = "https://api.edenic.io/api/v1/device/f73cdf90-8224-11ef-9338-8dff4b34f2dc"
#DEVICE_ATTRIBUTE_URL = "http://192.168.255.14:5000/device-attribute"
DEVICE_ATTRIBUTE_URL = "https://api.edenic.io/api/v1/device-attribute"
url = f"{DEVICE_ATTRIBUTE_URL}/21721bb0-82e6-11ef-98b7-63543a698b74"
api_token = "ed_5qbc89et3aqclsb19cvq4gahogjc0yuf9uoh0g0xyiuusump1c314z9rt6bjq9gk"

payload = {
    "setting.ph_low_alarm": 5.4,
    "setting.ph_high_alarm": 6.6,
    "setting.ec_low_alarm": 1.0,
    "setting.ec_high_alarm": 2.0,
    "setting.temp_low_alarm": 18,
    "setting.temp_high_alarm": 25,
    "setting.alarms": True,

}

headers = {
    "Authorization": f"{api_token}",
    "Content-Type": "application/json",
}

async def get_devices():
  async with aiohttp.ClientSession() as session:
    async with session.get(DEVICE_LIST_URL, headers=headers) as response:
      data = await response.json()
      print(data)

async def send_data():
  async with aiohttp.ClientSession() as session:
    async with session.patch(url, json=payload, headers=headers) as response:
      response.raise_for_status()  # Raise an exception for non-2xx status codes
      print(await response.text())

asyncio.run(get_devices())
asyncio.run(send_data())
