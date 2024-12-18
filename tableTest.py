#!/usr/bin/python

import rtmidi
from miditoolkit.midi import parser as mid_parser
import RPi.GPIO as GPIO
import math
import board
import neopixel
from mido import MidiFile
from tableHelpers import *

#####
## MIDI - from autoPopulate.py
#####
midPath = '/home/pi/Python/switchboard/peewee_populated.mid'
m=MidiFile(midPath)
midParsed = mid_parser.MidiFile(midPath)
g = (i for i, e in enumerate(midParsed.instruments) if e.name=="Game")
gameTrack = next(g) + 1
g = (i for i, e in enumerate(midParsed.instruments) if e.name=="Bells")
bellTrack = next(g) + 1

#####
## Native GPIO - 4 @ 12V relays, active LOW
#####
honk = digitalio.DigitalInOut(board.D27)
phone = digitalio.DigitalInOut(board.D17)
alarm = digitalio.DigitalInOut(board.D23)
unused = digitalio.DigitalInOut(board.D24)

for io in (honk, phone, alarm, unused):
    io.direction = digitalio.Direction.OUTPUT
    io.value = True

#####
## Neopixels - one strand for the whole table
#####
pixel_pin = board.D18
num_pixels = 160
ORDER = neopixel.GRB # RGB or GRB, changes addressing but commands are always RGB
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

### set up table (game starts all switches down)
for i in range(len(allSwitchBots)):
    pixels[allSwitchBots[i]] = color['amber']


#####
## initialize i2c GPIO expander
#####
print("initializing i2c")
i2c = busio.I2C(board.SCL, board.SDA)
mcp0 = MCP23017(i2c, address=0x20) # base address 0x20, A0-A2 set three LSB
# mcp1 = MCP23017(i2c, address=0x21)
# mcp2 = MCP23017(i2c, address=0x22)
pins0 = [] # gpio on mcp0
pins1 = [] # mcp1
pins2 = [] # mcp2
pinState0 = []
pinState1 = []
pinState2 = []

print("setting up mcp GPIO as input/pullup")
activeGPIO = (pins0) # (pins0, pins1, pins2)


for bank in activeGPIO:
    for p in range(16):
        bank.append(mcp0.get_pin(p))
        bank[p].direction = digitalio.Direction.INPUT
        bank[p].pull = digitalio.Pull.UP
print("i2c GPIOs initialized")

jackPinRange = range(0,10)
switchPinRange = range(10,14)

switchTargets=[]   
for i in range(len(activeGPIO)): 
    temp = []
    for j in range(len(orderMcp0)):
        temp.append(0)
    switchTargets.append(temp)  

mout = rtmidi.MidiOut()
ports = mout.get_ports()
print(ports)
mout.open_port(1)


for msg in m.play():
    if (msg.channel == gameTrack):
        for i in jackRange:
            if (msg.type == "note_off" and (msg.note == i + leadInSkip or msg.note== i + leadOutSkip)): # turn off LED if off in lead in/out
                pixels[jackLEDFromNote(msg.note)] = color['off']
            if (msg.type == "note_on" and (msg.note == i + leadInSkip)): # leadIn controls green ON (including solid green during actual target)
                pixels[jackLEDFromNote(msg.note)] = color['green']
            if (msg.type == "note_on" and (msg.note == i + leadOutSkip)): # leadOut controls red ON
                pixels[jackLEDFromNote(msg.note)] = color['red']
        for i in switchRange:
            if (msg.type == "note_off" and (msg.note == i + leadInSkip or msg.note== i + leadOutSkip)): # turn off both LEDs if off in lead in/out
                pixels[switchLEDFromNote(msg.note,'up')] = color['off']
                pixels[switchLEDFromNote(msg.note,'down')] = color['off']
            if (msg.type == "note_on" and (msg.note == i + leadInSkip)):    # turn on top if on in leadin
                pixels[switchLEDFromNote(msg.note, 'up')] = color['amber']
            if (msg.type == "note_on" and (msg.note == i + leadOutSkip)):   # turn on bottom if on in leadout
                pixels[switchLEDFromNote(msg.note, 'down')] = color['amber']
            if (msg.type == "note_off" and (msg.note == i)):
                pixels[switchLEDFromNote(msg.note, 'down')] = color['amber'] # turn on bottom if targeting note ends, this will override the off from the leadout

                
    elif (msg.channel == bellTrack):
        print("test")
    else:
        mout.send_message(msg.bytes())



        # for i in range(len(jackState)):
        #     if (msg.type == "note_off" and msg.note == jackNoteCenters[i]):
        #         jackState[i] = "grey"
        #         jackTargets[i] = -1
        #     elif (msg.type == "note_off" and msg.note == jackNoteCenters[i]+30):
        #         jackState[i] = 'grey'
        #     elif (msg.type == "note_off" and  msg.note == jackNoteCenters[i]+60):
        #         jackState[i] = 'grey'   
        #     elif (msg.type == "note_on" and msg.note == jackNoteCenters[i]+60):
        #         jackState[i] = "red"
        #     elif (msg.type == "note_on" and msg.note == jackNoteCenters[i]+30):
        #         jackState[i] = "green"
        #     elif (msg.type == "note_on" and msg.note == jackNoteCenters[i]):
        #         jackState[i] = "green"
        #         jackTargets[i] = 1
        if (msg.type == "note_on" and msg.note == checkNote):
            updateScore()
            jackTargets = [i * decayRate for i in jackTargets]
            
        updateScreen()
GPIO.cleanup()