#!/usr/bin/python

import board
import digitalio
import busio 
from time import sleep
import time
import neopixel
import sys

#####
## Neopixels
#####
color = {'red': (255,0,0), 'green': (0,255,0), 'off': (0,0,0), 'amber': (255,120,0), 'orange': (255,80,0), 'blue': (0,0,255), 'cyan': (0,255,255), 'violet':(255,0,255)}

if (len(sys.argv) == 1):
    pixColor = color['amber']
else:
    pixColor = color[sys.argv[1]]

pixel_pin = board.D18
num_pixels = 1
ORDER = neopixel.GRB # RGB or GRB, changes addressing but commands are always RGB
pixels = neopixel.NeoPixel(
    pixel_pin,
    num_pixels,
    auto_write=False,
    pixel_order = ORDER)

pixels[0] = pixColor
pixels.show()
