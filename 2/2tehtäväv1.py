from ssd1306 import SSD1306_I2C
from machine import Pin, PWM, I2C
import time


class LED: 
    def __init__(self, pin): # Parameter is the pin of the LED.
        self.led = Pin(pin, Pin.OUT) # Especify that is Pin.OUT
        self.pwm = PWM(self.led) # Adds the PWM
        self.state = False # Set as start value of the led "False", so they are off when program starts

class Button:
    def __init__(self, pin): # Parameter is the pin of the Button.
        self.button = Pin(pin, mode=Pin.IN, pull=Pin.PULL_UP) # Especify that is Pin.IN and PULL_UP (makes the default value of the button to be 1, unless it is pressed)
        
class Abort:
    def __init__(self, pin, leds): # Parameters are the pin of the abort button and the list with all the leds.
        self.button = Pin(pin, Pin.IN, Pin.PULL_UP) # Especify that is Pin.IN and PULL_UP
        self.button.irq(trigger=Pin.IRQ_FALLING, handler=self.handler_press) #irq method makes hardware send a signal to the processor that makes stop/interrupt its operations by using handler function.
        self.leds = leds #LEDs list

    def handler_press(self, pin):
        for led in self.leds: # It goes through the list turning off the LEDs
            led.state = False # Resets the state of the led to False.
            led.pwm.duty_u16(0) # Turns off the LEDs light using pwm.duty_u16.
            

i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000) # Initialice I2C bus object (transfer data between slave and master devices) using I2C() function. "1" parameter -> Uses the second I2C bus.
# sda & scl = pin objects, freq = 400 kHz
oled = SSD1306_I2C(128, 64, i2c) # SSD1306_I2C class represents the OLED display.
# 3 arguments: width (128px) and height (64px) of the display, and the I2C bus object that communicate with the display.

led1 = LED(20) # Runs LED class.
led2 = LED(21)
led3 = LED(22)

button1 = Button(9) # Runs Button class.
button2 = Button(8)
button3 = Button(7)

abort_button = Abort(12, [led1, led2, led3]) # Runs the Abort class using a list of the buttons as parameter.

while True:
    if button1.button.value() == 0: # When the button is pressed value=0..
        while button1.button.value() == 0: # while button is continuously pressed the program runs inside this sub-loop
            time.sleep(0.01) # This does nothing, is like "pass" but it does not require so much processing
        time.sleep(0.03) # takes a 0.03s break and prevents debounce (multiple presses).
        led1.state = not led1.state # changes the state from "off" to "on" and vice versa.
        if led1.state: # if the state is "on" (True) then turns on the light on.
            led1.pwm.duty_u16(1000) # light on using duty_u16(1000) so it is not too bright.
        else:
            led1.pwm.duty_u16(0) # light off.

    if button2.button.value() == 0:
        while button2.button.value() == 0:
            time.sleep(0.01)
        time.sleep(0.03)
        led2.state = not led2.state
        if led2.state:
            led2.pwm.duty_u16(1000)
        else:
            led2.pwm.duty_u16(0)

    if button3.button.value() == 0:
        while button3.button.value() == 0:
            time.sleep(0.01)
        time.sleep(0.03)
        led3.state = not led3.state
        if led3.state:
            led3.pwm.duty_u16(1000)
        else:
            led3.pwm.duty_u16(0)
            

    oled.fill(0) # Clear the OLED display
    
    
    oled.text("LED1: " + ("ON" if led1.state else "OFF"), 0, 0) # writes text to the frame buffer of the OLED display. Buffer = temporary storage area in memory that holds data.
    oled.text("LED2: " + ("ON" if led2.state else "OFF"), 0, 10) #first argument is specifies the text. 
    oled.text("LED3: " + ("ON" if led3.state else "OFF"), 0, 20) #second argument specifies the horizontal position of the text (position 0 on the x-axis).
    # third argument specifies the vertical position of the text (position 0/10/20 on the y-axis)
    
    oled.show() # Update the OLED display
