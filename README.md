# homeassistant-bluelab-guardian

![image](https://github.com/user-attachments/assets/9ca9d4ae-6a67-46b0-a47a-b5b9bf627586)

This custom HACS integration fetches telemetry data from Bluelab Edenic API. I'm using it with a Guardian Wifi.

PLEASE NOTE: the API is limited to one request per minute. Thus the interval of 70s is hard-coded, to make sure data fetching is successfull.

PLEASE NOTE2: unfortunately the Api only supports metric system. If you need for example your temperature in °F, you have to calculate it via a custom sensor or helper.

Just my 2 cents: This is one of the first integrations I'm working on. Quite sure that it can be better. Any contributions, recommendations and comments are welcome!

## Screenshot 

![image](https://raw.githubusercontent.com/maziggy/homeassistant-bluelab/refs/heads/main/custom_components/bluelab_guardian/screenshots/config.png)

## Installation

### Via HACS

1. Ensure you have [HACS](https://hacs.xyz/) installed.
2. In Home Assistant, go to **HACS** > **Frontend**.
3. Click the **"+"** button to add a new repository.
4. Enter the repository URL: `https://github.com/maziggy/homeassistant-bluelab.git`.
5. Select **Integration** as the category and **Save**.
6. Once installed, add the card to your Lovelace dashboard.

or simply

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=maziggy&repository=homeassistant-bluelab&category=integration)
