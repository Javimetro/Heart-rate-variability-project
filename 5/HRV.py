from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import ssd1306
import math

#OLED
i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# PPI values for testing
ppi_values = [828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812,812, 756, 820, 812, 800]
#[1000, 1100, 1000, 1100, 1000, 1100, 1000, 1100, 1000, 1100, 1000, 1100,1000, 1100, 1000, 1100, 1000, 1100, 1000, 1100]

# Calculating mean PPI and mean HR
mean_ppi = sum(ppi_values) / len(ppi_values)
mean_hr = 60000 / mean_ppi

# Calculating SDNN
sdnn = math.sqrt(sum([(x - mean_ppi)**2 for x in ppi_values]) / (len(ppi_values) - 1))

# Calculating RMSSD
rmssd = math.sqrt(sum([(x - y)**2 for x, y in zip(ppi_values[:-1], ppi_values[1:])]) / (len(ppi_values) - 1))

# Printing to OLED
oled.fill(0)
oled.text("PPI: {} ms".format(round(mean_ppi)), 0, 0)
oled.text("HR: {} bpm".format(round(mean_hr)), 0, 10)
oled.text("SDNN: {} ms".format(round(sdnn)), 0, 20)
oled.text("RMSSD: {} ms".format(round(rmssd)), 0, 30)
oled.show()
