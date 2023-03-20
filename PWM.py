from machine import Pin, PWM
import time


led1 = Pin(20, Pin.OUT)
pwm1 = PWM(led1)
led2 = Pin(21, Pin.OUT)
pwm2 = PWM(led2)
led3 = Pin(22, Pin.OUT)
pwm3 = PWM(led3)

led_sequence = [[0,0,0],[0,0,1],[0,1,0],[0,1,1],[1,0,0],[1,0,1],[1,1,0],[1,1,1]] 



while True:
    for leds in led_sequence:
        for duty in range(0, 16383, 100):
            pwm1.duty_u16(duty*leds[2])
            pwm2.duty_u16(duty*leds[1])
            pwm3.duty_u16(duty*leds[0])
            time.sleep(0.01)
        for duty in range(16383, -1, -100):
            pwm1.duty_u16(duty*leds[2])
            pwm2.duty_u16(duty*leds[1])
            pwm3.duty_u16(duty*leds[0])
            time.sleep(0.01)
            