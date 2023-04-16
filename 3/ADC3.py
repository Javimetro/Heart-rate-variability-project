from machine import ADC, Pin
from led import Led
from piotimer import Piotimer
from fifo import Fifo
import time

adc = ADC(26) # create an ADC object on pin 26
fifo = Fifo(100) # create a Fifo object with a size of 100
led = Led(20) # LED class so it is not too bright

last_sample = None # defaul value when starting = None
threshold = 50 # Limit for cleanin noises. If difference between values is smaller than this, then the value is not recorded in fifo
MAX_HISTORY = 250 # Max ammount of average values in the history list
history = [] #List with all the averages of the values.
beat = False # Default value for beat
beats = 0 # Start number of beats

def sample_data(timer): # Function to read signal with the sensor.
    global last_sample # Without the global keyword the sample_data function would create a new local variable called fifo instead of modifying the global fifo variable.
    sample = adc.read_u16() # read a sample from the ADC
    if last_sample is None or abs(sample - last_sample) > threshold:# Checks if the difference between the current sample and the last sample is > than 50 (threshold). If it is, it means that the current sample is different enough from the previous sample to be worth storing in the FIFO.
        fifo.put(sample) # add the raw ADC count value to the Fifo
        last_sample = sample # Updates the value of the last sample


window_size = 10 # size of moving window for calculating average
window_sum = 0 # sum of values in current window(0 at start)
window = [] # list to store fifo values in current window
 
timer = Piotimer(mode=Piotimer.PERIODIC, freq=250, callback=sample_data)# Piotimer object with a frequency of 250Hz and a callback function to sample data



def calculate_bpm(): # This function measures the beats per minute
    global beats # Gets updated value of the beats
    print('BPM:', beats * 6) # Triggered every 10 seconds, * 6 = bpm
    beats = 0 # Reset the beats

start_time = time.ticks_ms() # Software counter for calculate bpm (starts now)
interval = 10000 # 10 seconds in milliseconds




while True:
    # TIMER STARTS SO BPM CAN BE CALCULATED EVERY 10 SEC.
    current_time = time.ticks_ms() # this counter starts when while loop starts
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
                print("PUM")
                led.on() # turns the led on

            if beat and avg < threshold_off: # If the average is outside the beat´s threshold...
                beat = False # no beat :(
                led.off() # no light :(
            
