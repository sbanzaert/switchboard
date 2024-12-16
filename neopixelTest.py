#MUST RUN AS ROOT
import board
import neopixel
from time import sleep

pixel_pin = board.D18
num_pixels = 10
ORDER = neopixel.GRB # RGB or GRB
colors = ((255,0,0),(0,255,0),(0,0,255))

# pixels = neopixel.NeoPixel(board.D5, 30)    # Feather wiring!
pixels = neopixel.NeoPixel(
    pixel_pin,
    num_pixels,
    brightness=1,
    auto_write=True,
    pixel_order = ORDER)
while True:
    for n in range(num_pixels):
        pixels[n] = colors[n % 3]
        sleep(0.4)
        pixels[n] = (0,0,0)