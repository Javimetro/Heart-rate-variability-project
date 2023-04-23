from machine import Pin, PWM, I2C
from ssd1306 import SSD1306_I2C
import time

class LED: 
    def __init__(self, pin): # Parameter is the pin of the LED.
        self.led = Pin(pin, Pin.OUT) # Especify that is Pin.OUT
        self.pwm = PWM(self.led) # Adds the PWM
        self.state = False # Set as start value of the led "False", so they are off when program starts
        
class Rotary:
    def __init__(self, rot_A_pin, rot_B_pin, rot_button_pin, leds):
        self.rot_A_pin = Pin(rot_A_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.rot_B_pin = Pin(rot_B_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.rot_button_pin = Pin(rot_button_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.last_value_A = None
        self.position = 0
        self.leds = leds
        self.brightness_percentage = 0
        self.rotary_percentage = 0
        self.brightness_min = 0
        self.brightness_max = 65535
        self.brightness = 655
        menu_index = 0  # initialize menu_index to 0

    def select_led(self):
        i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
        oled = SSD1306_I2C(128, 64, i2c)
        led_options = ["LED1", "LED2", "LED3"]
        led_index = 0
        while True:
            oled.fill(0)
            for i in range(len(led_options)):
                oled.text('LED SELECTION',20,0)
                if i == led_index:
                    oled.text(">", 0, i * 10 + 20)
                oled.text(led_options[i], 10, i * 10 + 20)
            oled.show()
            value_A = self.rot_A_pin.value()
            value_B = self.rot_B_pin.value()
            value_button = self.rot_button_pin.value()
            
                  
            # Check for a rotation event
            if value_A != self.last_value_A:
                if value_B != value_A:
                    led_index += 1  # clockwise rotation
                else:
                    led_index -= 1  # counter-clockwise rotation

                # Ensure the selection stays within bounds
                if led_index < 0:
                    led_index = len(led_options) - 1
                elif led_index >= len(led_options):
                    led_index = 0

                # Display the current selection on the OLED screen
                oled.fill(0)
                for i in range(len(led_options)):
                    oled.text('LED SELECTION',20,0)
                    if i == led_index:
                        oled.text(">", 0, i * 10 + 20)
                    oled.text(led_options[i], 10, i * 10 + 20)
                oled.show()

            # Check for a button press event
            if not self.rot_button_pin.value():
                time.sleep(0.2)
                break

            # Update the last rotary value for the next iteration 
            self.last_value_A = value_A

            # Wait a short period before polling again
            time.sleep_ms(10)
            
        return self.leds[led_index]
    
        
    def menu_selection(self):
        i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
        oled = SSD1306_I2C(128, 64, i2c)
        menu_options = ["BRIGHTNESS", "LEDS"]
        menu_index = 0
        
        oled.fill(0)
        for i in range(len(menu_options)):
            oled.text('MENU',40,0)
            oled.text(menu_options[i], 10, i * 10 + 20)
        oled.show()
        while True:
            
            value_A = self.rot_A_pin.value()
            value_B = self.rot_B_pin.value()
            value_button = self.rot_button_pin.value()
            
            # Check for a rotation event
            if value_A != self.last_value_A:
                if value_B != value_A:
                    menu_index += 1  # clockwise rotation
                else:
                    menu_index -= 1  # counter-clockwise rotation
                
                # Ensure the selection stays within bounds
                if menu_index < 0:
                    menu_index = len(menu_options) - 1
                elif menu_index >= len(menu_options):
                    menu_index = 0
                
                # Display the current selection on the OLED screen
                oled.fill(0)
                for i in range(len(menu_options)):
                    oled.text('MENU',40,0)
                    if i == menu_index:
                        oled.text(">", 0, i * 10 + 20)
                    oled.text(menu_options[i], 10, i * 10 + 20)
                oled.show()
                 
            if not self.rot_button_pin.value():
                time.sleep(0.2)
                break
                    
            # Update the last rotary value for the next iteration
            self.last_value_A = value_A
            
            # Wait a short period before polling again
            time.sleep_ms(10)
        return menu_options[menu_index]
        
    def brightness_selection(self,led):
        i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
        oled = SSD1306_I2C(128, 64, i2c)
        oled.fill(0)
        oled.text("BRIGHTNESS", 0, 10)
        oled.show()
        menu_index = 0
        last_value_A = self.rot_A_pin.value()
        
        # Rotate the rotary encoder to adjust brightness
        while True:
            oled.fill(0)
            oled.text("BRIGHTNESS", 0, 10)
            oled.text(f"{self.brightness_percentage}%", 0, 30)
            oled.fill_rect(0, 50, int(self.brightness_percentage * 1.28), 10, 1)
            oled.show()
            
            value_A = self.rot_A_pin.value()
            value_B = self.rot_B_pin.value()
            value_button = self.rot_button_pin.value()
            
            if value_A != last_value_A:
                if value_B != value_A:
                    self.brightness += 1000
                else:
                    self.brightness -= 1000
                
                # Ensure the brightness stays within bounds
                if self.brightness < self.brightness_min:
                    self.brightness = self.brightness_min
                elif self.brightness > self.brightness_max:
                    self.brightness = self.brightness_max
                
                # Update the OLED display with the new brightness percentage
                self.brightness_percentage = int(
                    (self.brightness - self.brightness_min) / 
                    (self.brightness_max - self.brightness_min) * 100)
                
                # Change the brightness of the leds.
                duty_cycle = int((self.brightness_percentage / 100) * 65535)
                led.pwm.duty_u16(duty_cycle)

            
            if not value_button:
                # Wait for the button to be released before returning to the menu
                while not self.rot_button_pin.value():
                    pass
                break
            
            last_value_A = value_A
            time.sleep_ms(10)

def main(led):
    while True:
        menu = rotary.menu_selection()
        if menu == "BRIGHTNESS":
            brightness = rotary.brightness_selection(led)
        else:
            led = rotary.select_led()
            brightness = rotary.brightness_selection(led)
        
    
led1 = LED(20)
led2 = LED(21)
led3 = LED(22)
rotary = Rotary(10, 11, 12, [led1, led2, led3])    
led = rotary.select_led()
brightness = rotary.brightness_selection(led)
main = main(led)
