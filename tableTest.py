#!/usr/bin/python

import rtmidi
from miditoolkit.midi import parser as mid_parser
import RPi.GPIO as GPIO
import math
import board
import neopixel
import digitalio
import busio
from adafruit_mcp230xx.mcp23017 import MCP23017
from mido import MidiFile
from tableHelpers import *

#####
## MIDI - from autoPopulate.py
#####
midPath = '/home/pi/Python/switchboard/midi/peewee_populated.mid'
m=MidiFile(midPath)
midParsed = mid_parser.MidiFile(midPath)
g = (i for i, e in enumerate(midParsed.instruments) if e.name=="Game")
gameTrack = next(g) + 1
g = (i for i, e in enumerate(midParsed.instruments) if e.name=="Bells")
bellTrack = next(g) + 1

#####
## Native GPIO - 4 @ 12V relays, active LOW
#####
alarm = digitalio.DigitalInOut(board.D23) 
unused = digitalio.DigitalInOut(board.D24)
phone = digitalio.DigitalInOut(board.D25)
honk = digitalio.DigitalInOut(board.D8)
crankA = digitalio.DigitalInOut(board.D21) ## CHOSEN AT RANDOM, FIX IN PERSON
crankB = digitalio.DigitalInOut(board.D22)
for io in (honk, phone, alarm, unused, crankA, crankB):
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

mout = rtmidi.MidiOut()
ports = mout.get_ports()
print(ports)
mout.open_port(1)


for msg in m.play():
    if (msg.channel == gameTrack and hasattr(msg,'note')):
        print('is note!')
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
                pixels[switchLEDFromNote(msg.note, 'down')] = color['amber'] # turn on bottom when targeting note ends
        if msg.note == crankPitch + leadInSkip:
            if msg.type == "note_on":
                crankA.value = True
                crankB.value = False
            if msg.type == "note_off":
                crankA.value = True
                crankB.value = True
        if msg.type == "note_on" and msg.note in range(jackStart,crankPitch+1):
            updateTargetsFromNote(msg.note, True)
        if msg.type == "note_off" and msg.note in range(jackStart,crankPitch):
            updateTargetsFromNote(msg.note, False)
        if msg.note == testPointPitch and msg.type == "note_on":
            inputs = getStructuredGPIO(activeGPIO)
            updateScore(inputs, switchTargets)
            print (score)
    elif (msg.channel == bellTrack and hasattr(msg,'note')):
        
        if msg.note == bellPitch:
            if msg.type == "note_on":
                phone.value = True
            if msg.type == "note_off":
                phone.value = False
        if msg.note == alarmPitch:
            if msg.type == "note_on":
                alarm.value = True
            if msg.type == "note_off":
                alarm.value = False
        if msg.note == hornPitch:
            if msg.type == "note_on":
                honk.value = True
            if msg.type == "note_off":
                honk.value = False
    else:
        mout.send_message(msg.bytes())
#GPIO.cleanup()