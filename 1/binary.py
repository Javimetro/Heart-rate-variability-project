from machine import Pin
import time


led1 = Pin(20, Pin.OUT)
led2 = Pin(21, Pin.OUT)
led3 = Pin(22, Pin.OUT)

led_sequence = [[0,0,0],[0,0,1],[0,1,0],[0,1,1],[1,0,0],[1,0,1],[1,1,0],[1,1,1]] #every sublist is 1 second

while True:
    for leds in led_sequence: #every loop is one second
        led1.value(leds[2])
        led2.value(leds[1])
        led3.value(leds[0])
        time.sleep(1)