from datetime import timedelta

DOMAIN = "bluelab_guardian"
CONF_API_TOKEN = "api_token"
CONF_ORGANIZATION_ID = "organization_id"
DEVICE_LIST_URL = "https://api.edenic.io/api/v1/device/"
TELEMETRY_URL = "https://api.edenic.io/api/v1/telemetry/"
DEVICE_ATTRIBUTE_URL = "https://api.edenic.io/api/v1/device-attribute/"
TELEMETRY_UPDATE_INTERVAL = timedelta(seconds=70)
ATTRIBUTE_UPDATE_INTERVAL = timedelta(seconds=70)
