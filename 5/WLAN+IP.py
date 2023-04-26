import network
import socket
import time
import machine
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C

ssid = "KME670Group6"    # WiFi SSID
password = "NuuskaMuikkunen666"   # WiFi password

def connect():  # function for connect to the WLAN
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...') #If does not connect, this text is displayed
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

# OLED BUS
i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

try:
    ip = connect()
    oled.fill(0)
    oled.text("Connected to IP:", 0, 10)
    oled.text(ip, 0, 30)
    oled.show()
    
    
except OSError as e: #If there is not connection, error message is displayed.
    print("Error connecting to WiFi:", e)
    machine.reset()
