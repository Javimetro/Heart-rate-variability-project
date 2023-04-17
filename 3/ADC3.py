from machine import ADC, Pin, I2C
from led import Led
from piotimer import Piotimer
from fifo import Fifo
from ssd1306 import SSD1306_I2C
import time

#VARIABLES AND LISTS
adc = ADC(26) # create an ADC object on pin 26
fifo = Fifo(100) # create a Fifo object with a size of 100
led = Led(20) # LED class so it is not too bright
last_sample = None # defaul value when starting = None
threshold = 50 # Limit for cleanin noises. If difference between values is smaller than this, then the value is not recorded in fifo
MAX_HISTORY = 250 # Max ammount of average values in the history list
history = [] #List with all the averages of the values.
beat = False # Default value for beat
beats = 0 # Start number of beats
window_size = 10 # size of moving window for calculating average
window_sum = 0 # sum of values in current window(0 at start)
window = [] # list to store fifo values in current window

#SAMPLE_DATA FUNCTION
def sample_data(timer): # Function to read signal with the sensor.
    global last_sample # Without the global keyword the sample_data function would create a new local variable called fifo instead of modifying the global fifo variable.
    sample = adc.read_u16() # read a sample from the ADC
    if last_sample is None or abs(sample - last_sample) > threshold:# Checks if the difference between the current sample and the last sample is > than 50 (threshold). If it is, it means that the current sample is different enough from the previous sample to be worth storing in the FIFO.
        fifo.put(sample) # add the raw ADC count value to the Fifo
        last_sample = sample # Updates the value of the last sample
        
# HARDWARE TIMER FOR SAMPLE_DATA FUNCTION
timer = Piotimer(mode=Piotimer.PERIODIC, freq=250, callback=sample_data)# Piotimer object with a frequency of 250Hz and a callback function to sample data

#CALCULATE_BPM FUNCTION
def calculate_bpm(): # This function measures the beats per minute
    global beats # Gets updated value of the beats
    print('BPM:', beats * 6) # Triggered every 10 seconds, * 6 = bpm (This can be easly regulate if more precise measurement is needed)
    beats = 0 # Reset the beats

#SOFTWARE COUNTER FOR CALCULATE_BPM FUNCTION
start_time = time.ticks_ms() # Software counter for calculate bpm (starts now)
interval = 10000 # 10 seconds in milliseconds (This can be easly regulate if more precise measurement is needed)

#OLED SCREEN
i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000) # Initialice I2C bus object (transfer data between slave and master devices) using I2C() function. "1" parameter -> Uses the second I2C bus.
# sda & scl = pin objects, freq = 400 kHz
oled = SSD1306_I2C(128, 64, i2c) # SSD1306_I2C class represents the OLED display.
# 3 arguments: width (128px) and height (64px) of the display, and the I2C bus object that communicate with the display.

# HEART SHAPE MATRIX
HEART = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 1, 1, 0],
    [1, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0]
]


scale = 6 # scaling factor for the heart shape

# Scale up the heart shape matrix
heart_shape = [] # create an empty list to hold the scaled-up heart shape matrix.
for row in HEART: # iterate through each row in the HEART matrix.
    heart_row = [] # create an empty list to hold the scaled-up pixels for the current row.
    for pixel in row: # iterate trough each pixel in the current row.
        heart_row += [pixel] * scale # append scale copies of the current pixel to the heart_row list.
    heart_shape += [heart_row] * scale # append scale copies of the current row (i.e., the heart_row list) to the heart_shape list.

#LOOP STARTS
while True:
    
    # TIMER STARTS SO BPM CAN BE CALCULATED EVERY 10 SEC.
    current_time = time.ticks_ms() # this counter starts when loop starts
    elapsed_time = time.ticks_diff(current_time, start_time) # calculates the time difference between the current time and the start time. Start time is when script starts running
    if elapsed_time >= interval: # if 10 sec has gone then bpm can be calculated
        calculate_bpm() # calculates bpm
        start_time = current_time # counter reseted
        
    # HERE STARTS THE ALGORITHM TO FIND THE PEAKS OF THE VALUES    
    if not fifo.empty(): # if there are values in fifo...
        adc_count = fifo.get() # get the raw ADC count value from the Fifo
        window.append(adc_count) # add the value to the current window
        window_sum += adc_count # add the value to the sum of the window
        
        if len(window) > window_size: # if the window is full...
            window_sum -= window.pop(0) # remove the oldest value from the window and subtract it from the sum
            
        if len(window) == window_size: # if the window is full...
            avg = window_sum / window_size # calculate the average of the values in the window
            #print(avg) # print the average value
            history.append(avg) # add the average value to the history list

            # Get the tail, up to MAX_HISTORY length
            history = history[-MAX_HISTORY:] #ensures that the history list does not grow too large (>250) and consumes too much memory.
            # [-MAX_HISTORY:] slicing notation. It means "give me a slice of the list that starts from the MAX_HISTORY:th element from the end of the list, and includes all the elements up to the end of the list.

            minima, maxima = min(history), max(history) # creates 2 variables with the min and max values of the list

            threshold_on = (minima + maxima * 3) // 4   # 3/4 of the maximum value. Here is the heart´s beat!
            threshold_off = (minima + maxima) // 2      # 1/2 of the maximum value

            if not beat and avg > threshold_on: # If the average is inside the beat´s threshold...
                beat = True # There is beat! :)
                beats += 1 # Add it
                print(f'PIM-PUM {beats}')
                for y, row in enumerate(heart_shape): # y is the index of the line, so the loop goes trough every line starting from 0 (first line of the shape).
                    for x, pixel in enumerate(row): # x is the index of the pixel, so the loop goes trough every pixel of the line starting from 0 (first pixel of the line).
                        if pixel:
                            oled.fill_rect(x, y, 1, 1, 1) # fills "x" pixels form the left edge and "y" pixels from the top of the screen with coloured pixels.
                            # .fill_rect method: fills a rectangle. x and y are the cordinates of the rectangle, first 2 ones (1,1...) are the width and height of the rectangle in pixels. Last number one (...1) is the colour value.
                #oled.text("PIM-PUM", 0, 0)
                oled.show()
                led.on() # turns the led on

            if beat and avg < threshold_off: # If the average is outside the beat´s threshold...
                beat = False # no beat :(
                oled.fill(0) # Clear the OLED display
                oled.show()
                led.off() # no light :(
