import math
import board
import neopixel
import digitalio
import busio 
from adafruit_mcp230xx.mcp23017 import MCP23017
from mido import MidiFile
from tableHelpers import *

#####
## Neopixels - one strand for the whole table
#####
pixel_pin = board.D18
num_pixels = 160
ORDER = neopixel.GRB # RGB or GRB, changes addressing but commands are always RGB
pixels = neopixel.NeoPixel(
    pixel_pin,
    num_pixels,
    auto_write=False,
    pixel_order = ORDER)
print("clearing pixels")
for p in range(num_pixels):
    pixels[p] = color['off']
pixels.show()
print("pixels cleared")

### set up table (game starts all switches down)
for i in range(len(allSwitchBots)):
    pixels[allSwitchBots[i]] = color['amber']
pixels.show()

#####
## initialize i2c GPIO expander
#####
print("initializing i2c")
i2c = busio.I2C(board.SCL, board.SDA)
mcp0 = MCP23017(i2c, address=0x20) # base address 0x20, A0-A2 set three LSB
mcp1 = MCP23017(i2c, address=0x21)
mcp2 = MCP23017(i2c, address=0x22)
GPIObanks = [mcp0, mcp1, mcp2]
activeGPIO = []

print("setting up mcp GPIOs as input/pullup")

## want: activeGPIO = [[mcp0.get_pin(0), mcp0.get_pin(1)...], [mcp1.get_pin(0),...]]
for i in range(len(GPIObanks)):
        activeGPIO.append([])
        for p in range(15):
            activeGPIO[i].append(GPIObanks[i].get_pin(p))
            if p == 7 or p == 15:
                activeGPIO[i][p].direction = digitalio.Direction.OUTPUT    
            else:
                activeGPIO[i][p].direction = digitalio.Direction.INPUT
                activeGPIO[i][p].pull = digitalio.Pull.UP
print("i2c GPIOs initialized")

switchTargets=[]   
for i in range(len(activeGPIO)): 
    temp = []
    for j in range(len(orderMcp0)):
        temp.append(0)
    switchTargets.append(temp)  

def updateTargetsFromNote(pitch: int, v: bool):
    global switchTargets
    if pitch in jackRange:
        bank = math.floor((pitch-jackStart)/10)
        switchTargets[bank][pitch % 10] = v
    if pitch in switchRange:
        bank = math.floor((pitch-switchStart)/4)
        switchTargets[bank][(pitch-switchStart) % 4] = v
    if pitch == crankPitch:
        switchTargets[2][13] = v # use unused part of bank 2 for crank data

while True:
    