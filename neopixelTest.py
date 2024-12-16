#MUST RUN AS ROOT
import board
import neopixel
from time import sleep
import random

pixel_pin = board.D18
num_pixels = 145
ORDER = neopixel.GRB # RGB or GRB
colors = ((255,0,0),(0,255,0),(0,0,255))
skips = list(range(10,17)) + list(range(27,34)) + list(range(44,51)) + list(range(61,68)) + list(range(78,85))+list(range(95,103))+list(range(113,120))+list(range(130,135))

pixels = neopixel.NeoPixel(
    pixel_pin,
    num_pixels,
    brightness=1,
    auto_write=True,
    pixel_order = ORDER)

# pixList = (0,1,2,3,4)
# while True:
#     for i in range(len(pixList)):
#         pixList[i] = random.randint(0,num_pixels-1)
#         if pixList[i] in skips:
#             pixels[pixList[i]]=(0,0,0)    
#         else:
#             pixels[pixList[i]] = colors[n % 3]
#     for i in pixList.__len__():
#         sleep(0.1)
#         pixels[pixList[i]] = (0,0,0)
        
# for n in pixel_tests:
#     pixels[n] = (255,0,0)
#     sleep(0.5)
#     pixels[n] = (0,0,0)

while True:
    for n in range(num_pixels):
        if n in skips:
            pixels[n] = (0,0,0)
        else:
            pixels[n] = colors[n % 3]
            sleep(0.075)
            #pixels[n] = (0,0,0)