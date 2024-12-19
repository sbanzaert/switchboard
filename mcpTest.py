# https://learn.adafruit.com/adafruit-mcp23017-i2c-gpio-expander/python-circuitpython
# pip install adafruit-citcuitpython-mcp230xx

import board
import busio
import digitalio
from time import sleep

from adafruit_mcp230xx.mcp23017 import MCP23017

i2c = busio.I2C(board.SCL, board.SDA)
mcp0 = MCP23017(i2c, address=0x20) # base address 0x20, A0-A2 set three LSB
mcp1 = MCP23017(i2c, address=0x21)
mcp2 = MCP23017(i2c, address=0x22)

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

orderMcp0 = [0,1,2,3,4,8,9,10,11,12,5,6,13,14] # {jacks 0-9} {switches 0-3} - 7 & 15 not used, 14 reserved for hand crank
orderMcp1 = [0,1,2,3,4,8,9,10,11,12,5,6,13,14] # {jacks 0-9} {switches 0-3}
orderMcp2 = [0,1,2,3,4,8,9,10,11,12,5,6,13,14] # {jacks 0-9} {switches 0-3} {hand crank}
mcpOrders = (orderMcp0, orderMcp1, orderMcp2)

def getOrderedPinState(pinArray, pinOrderArray):
    pinState=[]
    for p in range(15):
        # print("p: {} ps0: {}".format(p, pinState0[p]))
        pinState.append(pinArray[p].value) # True = plugged in, need to check switches
    pinState = [pinState[i] for i in pinOrderArray]
    return pinState

def getStructuredGPIO(GPIOarray):
    out = []
    for s in range(len(GPIOarray)):
        out.append(getOrderedPinState(GPIOarray[s],mcpOrders[s]))
    return out
while True:
    for i in range(3):
        print (getStructuredGPIO(activeGPIO)[i])
    print("--------")
    sleep(.5)

# while(True):
#     print(pin0.value)
#     sleep(0.1)

# for p in range(15):
#     mcp.get_pin(p).direction = digitalio.Direction.INPUT
#     mcp.get_pin(p).pull = digitalio.Pull.UP
#     print(str(p) + ": " str(mcp.get_pin(p).value))
# pins = []
# for p in range(16):
#     pins.append(mcp0.get_pin(p))
#     pins[p].direction = digitalio.Direction.INPUT
#     pins[p].pull = digitalio.Pull.UP
#     print("{0}: {1}".format(p, pins[p].value))
