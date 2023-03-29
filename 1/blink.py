from led import Led
from machine import Pin
import time


led1 = Led(20)
led2 = Led(21)
led3 = Led(22)

led_sequence = [[0,0,0],[0,0,1],[0,1,0],[1,0,0]] #every sublist is 1 second

while True:
    for leds in led_sequence: #every loop is one second
        led1.value(leds[2])
        led2.value(leds[1])
        led3.value(leds[0])
        time.sleep(1)
