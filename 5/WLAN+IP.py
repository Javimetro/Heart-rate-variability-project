import network
import socket
import time
import machine
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C

ssid = "KME670Group6"    # Enter your WiFi SSID here
password = "NuuskaMuikkunen666"   # Enter your WiFi password here

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

try:
    ip = connect()
    oled.fill(0)
    oled.text("Connected to IP:", 0, 10)
    oled.text(ip, 0, 30)
    oled.show()
    
    
except OSError as e:
    print("Error connecting to WiFi:", e)
    machine.reset()