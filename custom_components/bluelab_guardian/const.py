from datetime import timedelta

DOMAIN = "bluelab_guardian"
CONF_API_TOKEN = "api_token"
CONF_ORGANIZATION_ID = "organization_id"
DEVICE_LIST_URL = "http://192.168.255.14:5000/organization_id/"
TELEMETRY_URL = "http://192.168.255.14:5000/telemetry/"
DEVICE_ATTRIBUTE_URL = "http://192.168.255.14:5000/attributes/"
TELEMETRY_UPDATE_INTERVAL = timedelta(seconds=70)
ATTRIBUTE_UPDATE_INTERVAL = timedelta(seconds=70)
