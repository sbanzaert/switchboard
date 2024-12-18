# https://learn.adafruit.com/adafruit-mcp23017-i2c-gpio-expander/python-circuitpython
# pip install adafruit-citcuitpython-mcp230xx

import board
import busio
import digitalio
from time import sleep

from adafruit_mcp230xx.mcp23017 import MCP23017

i2c = busio.I2C(board.SCL, board.SDA)
mcp0 = MCP23017(i2c, address=0x20) # base address 0x20, A0-A2 set three LSB
# mcp1 = MCP23017(i2c, address=0x21)
# mcp2 = MCP23017(i2c, address=0x22)

pin0 = mcp0.get_pin(0) #0-15 for 23017
pin0.direction = digitalio.Direction.INPUT
pin0.pull = digitalio.Pull.UP

# while(True):
#     print(pin0.value)
#     sleep(0.1)

# for p in range(15):
#     mcp.get_pin(p).direction = digitalio.Direction.INPUT
#     mcp.get_pin(p).pull = digitalio.Pull.UP
#     print(str(p) + ": " str(mcp.get_pin(p).value))
pins = []
for p in range(16):
    pins.append(mcp0.get_pin(p))
    pins[p].direction = digitalio.Direction.INPUT
    pins[p].pull = digitalio.Pull.UP
    print("{0}: {1}".format(p, pins[p].value))
