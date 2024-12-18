# Incoming data format:
# {jack1-5} {sw1-2} x {jack6-10} {sw3-4} x


import board
import busio
import digitalio
from time import sleep
import neopixel
from adafruit_mcp230xx.mcp23017 import MCP23017

print("Starting....")
#####
## initialize GPIO expander
#####
i2c = busio.I2C(board.SCL, board.SDA)
mcp0 = MCP23017(i2c, address=0x20) # base address 0x20, A0-A2 set three LSB
pins0 = []
pins1 = []
pins2 = []
pinState0 = []
pinState1 = []
pinState2 = []
orderMcp0 = [0,1,2,3,4,8,9,10,11,12,5,6,13,14] # {jacks 0-9} {switches 0-3}

jackPinRange = range(0,10)
switchPinRange = range(10,14)

print("i2c initialized")
#####
## initialize neopixels
#####
pixel_pin = board.D18
num_pixels = 160
ORDER = neopixel.GRB # RGB or GRB, changes addressing but commands are always RGB
color = {'red': (255,0,0), 'green': (0,255,0), 'off': (0,0,0), 'amber': (255,120,0)}
pixels = neopixel.NeoPixel(
    pixel_pin,
    num_pixels,
    brightness=1,
    auto_write=True,
    pixel_order = ORDER)
print("clearing pixels")
for p in range(num_pixels):
    pixels[p] = color['off']
print("pixels cleared")

def rToL(a: int,b: int ):
    return list(range(a,b))
### pixel addresses w/ wired switches
### same ordering as pinState
activePanel1 = ( 0, 2, 5, 8, 9,94,92,89,87,86) ## pinState0
activePanel2 = (18,20,22,25,26,77,74,73,71,69)
activePanel3 = (34,36,37,41,43,60,57,56,53,52)
activeSwitch1top=(104,105,109,112)
activeSwitch1bot=(158,157,153,150)
activeSwitch2top=(120,122,123,124)
activeSwitch2bot=(144,142,141,136)

allJack1 = rToL(0,10) + rToL(86,95)[::-1]
allJack2 = rToL(17,27) + rToL(68,78)[::-1]
allJack3 = rToL(34,44) + rToL(51,61)[::-1]
allSwitch1top = rToL(103,113)
allSwitch2top = rToL(120,130)
allSwitch1bot = rToL(150,160)[::-1]
allSwitch2bot = rToL(135,144)[::-1]
print("setting up pins")
for p in range(16):
    pins0.append(mcp0.get_pin(p))
    pins0[p].direction = digitalio.Direction.INPUT
    pins0[p].pull = digitalio.Pull.UP


print("entering loop")
while True:
    print("top of loop")
    pinState0=[]
    for p in range(16):
        # print("p: {} ps0: {}".format(p, pinState0[p]))
        pinState0.append(pins0[p].value) 
    pinState0 = [pinState0[i] for i in orderMcp0]

    for i in jackPinRange:
        if pinState0[i] == True:
            pixels[activePanel1[i]] = color['green']
        else:
            pixels[activePanel1[i]] = color['red']
# for p in activePanel1:
#     pixels[p] = color['amber']

# for p in allSwitch1bot + allSwitch2bot:
#     pixels[p]= color['amber']
# for i in range(5):
#     for p in activeSwitch1bot:
#         pixels[p] = color['amber']
#     sleep(.5)
#     for p in activeSwitch1bot:
#         pixels[p] = color['off']
#     sleep(.5)