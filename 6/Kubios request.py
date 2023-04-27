import urequests as requests
import ujson
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C

### FIRST WLAN CONNECTION MUST BE CREATED BY RUNNING THE CODE IN ASSIGNMENT 5 ("WLAN+IP.py") ###

# Variables
APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"
LOGIN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/login"
TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token"
REDIRECT_URI = "https://analysis.kubioscloud.com/v1/portal/login"

#OLED BUS
i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# Trying the request.
try:
    # Get access token using client credentials grant
    response = requests.post(
        url=TOKEN_URL,
        data="grant_type=client_credentials&client_id={}".format(CLIENT_ID),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    response = response.json()
    access_token = response["access_token"]

    # Data set for Kubios API request
    data_set = {
        "type": "RRI",
        "data": [
            828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800
        ],
        "analysis": {
            "type": "readiness"
        }
    }

    # Request to Kubios API
    response = requests.post(
        url="https://analysis.kubioscloud.com/v2/analytics/analyze",
        headers={
            "Authorization": "Bearer {}".format(access_token),
            "X-Api-Key": APIKEY
        },
        json=data_set
    )
    response = response.json()

    # Secetion of wanted values
    sns_index = response['analysis']['sns_index']
    pns_index = response['analysis']['pns_index']
    
    print("SNS index:", sns_index)
    print("PNS index:", pns_index)

    oled.fill(0)
    oled.text(f"SNS: {sns_index}", 0, 10)
    oled.text(f"PNS: {pns_index}", 0, 20)
    oled.show()
    
# Error information
except Exception as e:
    print("Error occurred while making request to Kubios API:", e)
    oled.fill(0)
    oled.text(f"ERROR: {e}", 0, 10)
    oled.show()
