import network
import socket
import time
import machine
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C

#ssid = "KME670Group6"    # WiFi SSID
#password = "NuuskaMuikkunen666"   # WiFi password

class Netti:
    def __init__(self, SSID, password):  # function for connect to the WLAN
        self.SSID = SSID
        self.password = password
        wlan = network.WLAN(network.STA_IF)
        i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
        oled = SSD1306_I2C(128, 64, i2c)
        #Connect to WLAN
        
        wlan.active(True)
        wlan.connect(self.SSID, self.password)
        try: 
            while wlan.isconnected() == False:
                print('Waiting for connection...') #If does not connect, this text is displayed
                oled.fill(0)
                oled.text("Waiting for", 0, 10)
                oled.text("internet", 0, 20)
                oled.text("connection...", 0, 30)
                oled.show()
                time.sleep(1)
            ip = wlan.ifconfig()[0]
            print(f'Connected on {ip}')
            oled.fill(0)
            oled.text("Connected to IP:", 0, 10)
            oled.text(ip, 0, 20)
            oled.text("PRESS BUTTON", 0, 40)
            oled.show()
            
        except OSError as e: #If there is not connection, error message is displayed.
            print("Error connecting to WiFi:", e)
            machine.reset()
        if wlan.isconnected():
            print("Pico is connected to the WLAN")
        else:
            print("Pico is not connected to the WLAN")
            

# connect = Netti("Koti_F11D","HLMGF8NFC3FPE")

    
