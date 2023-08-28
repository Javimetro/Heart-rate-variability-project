from machine import Pin, PWM, I2C
import network
from piotimer import Piotimer
from fifo import Fifo
import utime
import urequests as requests
import ujson
from heart import PPI
from class_Netti import Netti

# Variables
APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"
LOGIN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/login"
TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token"
REDIRECT_URI = "https://analysis.kubioscloud.com/v1/portal/login"
rot_button_pin = Pin(12, Pin.IN, Pin.PULL_UP)

#in the PPI class create the adc instance
ppi = PPI(26)
tmr = Piotimer(mode = Piotimer.PERIODIC, freq = 250, callback = ppi.insert_samples)
utime.sleep(2)
#call the function that counts the PPI values for kubios and displays the heart image to oled (sydän jostain syystä näkyy nyt kokoajan eikä vilku)

connect = Netti("KME670Group6","NuuskaMuikkunen666")
utime.sleep(3)

while True:
    if not rot_button_pin.value():
        ppi.oled.fill(0)
        ppi.oled.text(f"ANALYZING...", 0, 10)
        ppi.oled.show()
        try:
            ppi.collect_data()
            print('Sending data to Kubios...')
            ppi.oled.fill(0)
            ppi.oled.text(f"SENDING DATA", 0, 10)
            ppi.oled.text(f"TO KUBIOS...", 0, 20)
            ppi.oled.show()
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
                "data": ppi.kubios, #adding the list of 20 PPIs to be sent
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
            hr_bpm = response['analysis']['mean_hr_bpm']
            sns_index = response['analysis']['sns_index']
            pns_index = response['analysis']['pns_index']
            print('HR bpm', hr_bpm)
            print("SNS index:", sns_index)
            print("PNS index:", pns_index)

            ppi.oled.fill(0)
            ppi.oled.text(f"RESULTS:", 30, 10)
            ppi.oled.text(f"HR: {hr_bpm} bpm", 0, 30)
            ppi.oled.text(f"SNS: {sns_index}", 0, 40)
            ppi.oled.text(f"PNS: {pns_index}", 0, 50)
            
            ppi.oled.show()
            
        # Error information
        except Exception as e:
            print("Error occurred while making request to Kubios API:", e)
            ppi.oled.fill(0)
            ppi.oled.text(f"ERROR: {e}", 0, 10)
            ppi.oled.show()