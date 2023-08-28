from machine import ADC, Pin, I2C
from piotimer import Piotimer
from fifo import Fifo
import utime
from ssd1306 import SSD1306_I2C


class PPI():
    def __init__(self, pin_nr):
        self.i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
        self.oled = SSD1306_I2C(128, 64, self.i2c)
        self.av = ADC(pin_nr) # sensor AD channel
        self.ave_fifo = Fifo(50)
        self.samples = Fifo(500) # buffer
        self.kubios=[]
        self.count=0
        self.beat=False
        self.beat_detected=0
        self.heart = [
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


    # Scale up the heart shape matrix
   # heart_shape = [] # create an empty list to hold the scaled-up heart shape matrix.
# append scale copies of the current row (i.e., the heart_row list) to the heart_shape list.
    def display_heart(self):
        heart_shape=[]
        for row in self.heart: # iterate through each row in the HEART matrix.
            heart_row = [] # create an empty list to hold the scaled-up pixels for the current row.
            for pixel in row: # iterate trough each pixel in the current row.
                heart_row += [pixel] * 6 # append scale copies of the current pixel to the heart_row list.
            heart_shape += [heart_row] * 6 
        for y, row in enumerate(heart_shape): # y is the index of the line, so the loop goes trough every line starting from 0 (first line of the shape).
            for x, pixel in enumerate(row): # x is the index of the pixel, so the loop goes trough every pixel of the line starting from 0 (first pixel of the line).
                if pixel:
                    self.oled.fill_rect(x, y, 1, 1, 1) # fills "x" pixels form the left edge and "y" pixels from the top of the screen with coloured pixels.

        
        
    #function to put the samples into the large fifo automatically (2seconds of data)
    def insert_samples(self, pin):
        self.samples.put(self.av.read_u16())
        
    #function for counting the PPIs for Kubios and displaying the heart  
    def collect_data(self):
        previous_bpm=0
        bpm=0
        self.kubios =[] #aina kun tähän funktioon tullaan niin tyhjennetään kubiokselle lähettettävä lista, jos siellä oiski aiemmat arvot tallessa
        while True:
            if not self.samples.empty():
                value = self.samples.get()
                #add value to ave_fifo from the main fifo
                self.ave_fifo.put(value)
                value= self.ave_fifo.get()
                #ave_fifi.data pääsee käsiksi bufferissa oleviin arvoihin, lasketaan siis keskiarvo pienestä fifosta, siistii vaan signaalia
                average= (sum(self.ave_fifo.data)) / 50
                #asetetaan raja-arvo datan keskiarvon kohdalle, tällä "nollataan" syke (raja-arvo on siis isomman fifon keskiarvo)
                threshold_under = (sum(self.samples.data)) / 500
                #toinen raja-arvo vähän sykedatan yläpuolelle,tätä käytetään sykkeen havaitsemiseen
                #koska signaali saattaa vähän heitellä on parempi että on kaks raja-arvoa mitä käytetään seuraamiseen
                threshold=threshold_under*1.02
                #seurataan sampleja
                self.count+=1
                #jos signaali siirtyy korkeamman raja-arvon yläpuolelle kun sykettä ei ole havaittu
                if average>threshold and self.beat==False:
                    self.beat=True
                    #intervalli on tän hetkisen samplen nro-viime kerta kun syke havaittu
                    interval=self.count-self.beat_detected
                    peak=interval*4
                    #samplen nro talteen, jolla nyt havaittiin syke
                    self.beat_detected= self.count
                    #vain jos sykkeen arvo on välillä 30-200 laskee sykkeen arvon bpm muuttujassa
                    if interval<500 and interval>75:
                        #syke = 60s / (millisekuntit viime sykehavainnosta/1000)
                        bpm=round(60/((interval*4)/1000))
                        if abs(bpm-previous_bpm)<10:
                            print(bpm)
                            self.kubios.append(peak)
                if average<threshold_under and self.beat==True:
                    self.beat=False
                    previous_bpm=bpm
                #when 20 values are gathered to Kubios, stop gathering data
                if len(self.kubios)==20:
                    return


            
