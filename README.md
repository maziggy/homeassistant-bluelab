# homeassistant-bluelab-guardian

![image](https://github.com/user-attachments/assets/9ca9d4ae-6a67-46b0-a47a-b5b9bf627586)

This custom HACS integration fetches telemetry data from Bluelab Edenic API. I'm using it with a Guardian Wifi.

PLEASE NOTE: the API is limited to one request per minute. Thus the interval of 70s is hard-coded, to make sure data fetching is successfull.

Just my 2 cents: This is one of the first integrations I'm working on. Quite sure that it can be better. Any contributions, recommendations and comments are welcome!

## Screenshot 

![image](https://github.com/user-attachments/assets/3a892a36-6592-4f7d-aca9-0d00e5ee84e9)

## Installation

### Via HACS

1. Ensure you have [HACS](https://hacs.xyz/) installed.
2. In Home Assistant, go to **HACS** > **Frontend**.
3. Click the **"+"** button to add a new repository.
4. Enter the repository URL: `https://github.com/maziggy/homeassistant-bluelab.git`.
5. Select **Dashboard** as the category and **Save**.
6. Once installed, add the card to your Lovelace dashboard.

or simply

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=%40maziggy&repository=https%3A%2F%2Fgithub.com%2Fmaziggy%2Fhomeassistant-bluelab&category=Integration)
