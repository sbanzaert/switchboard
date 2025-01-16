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
import serial
import collections
from pythonosc.udp_client import SimpleUDPClient
from time import sleep
import time


ser = serial.Serial("/dev/ttyUSB0")

gameMode = 'hard'
handCrank = 1

#####
## logging
#####
logFn = "./logs/" + time.strftime("%m-%d-%H%M") + "-alldata.txt"
scoreFn = "./logs/" + time.strftime("%m-%d-%H%M") + "-scores.txt"
print(logFn)

with open(logFn, 'w', encoding="utf=8") as f:
    f.write("Log started " + time.strftime("%m-%d--%H%M")+"\n")
with open(scoreFn, 'w', encoding="utf=8") as f:
    f.write("Log started " + time.strftime("%m-%d--%H%M")+"\n")
#####
## puredata OSC routines
#####
ip = '127.0.0.1'
port = 1337
PDclient = SimpleUDPClient(ip,port)

rvb = 0.5
lpf = 100
scoreRange = [0, 1]
mid_score = sum(scoreRange)/2

#ranges are in format [bad,good]
LPFranges = {'easy': [1000,2000], 'medium': [500,2000], 'hard': [40, 2000]} # modified from 80/.5 for last run Sunday
reverbRanges = {'easy': [.1,0], 'medium': [.3,0], 'hard': [.5,0]}
staticRanges = {'easy': [.2,0], 'medium': [.4,0], 'hard': [.6, 0]} #

def remap(x, range1, range2):
    d1 = range1[1]-range1[0]
    d2 = range2[1]-range2[0]
    return (d2 * (x - range1[0])/d1) + range2[0]

def updatePuredata(s: float, difficulty: str):
    # map score to LPF value
    lpf = remap(s, scoreRange, LPFranges[difficulty])
    static = remap(s, scoreRange, staticRanges[difficulty])
    if score <= mid_score:
        rvb = remap(s, [scoreRange[0], mid_score], reverbRanges[difficulty])
    else: rvb = 0
    PDclient.send_message("/test",[.5,rvb,lpf,0]) # don't intentionally start PD
    print (str(score) + ", " + str(lpf) + ", " + str(rvb))



#####
## Game setup
#####
startingScore = scoreRange[0]+ (scoreRange[1]-scoreRange[0])/3
score = startingScore # percentage score
prevScore = score
fallGain = 0.3 # peak detector w/ fadeaway, gain 0->1
scoringHistory = 2 * 4 # scoring done in ticks, one per quarter note, this is ticksPerBar * bars
initScoreDataGood = []
initScoreDataBad = []
for i in range(scoringHistory): # initialize to a full scoring history of neutrality
    initScoreDataBad.append(0)
    initScoreDataGood.append(0)
 
correct_passive = collections.deque(initScoreDataGood, scoringHistory) # need no action, did no action
correct_active = collections.deque(initScoreDataGood, scoringHistory) # need action, did action
wrong_removal = collections.deque(initScoreDataBad, scoringHistory) # need no action, did action
wrong_noAct = collections.deque(initScoreDataBad, scoringHistory) # need action, did no action
totalTests = collections.deque(initScoreDataBad, scoringHistory) # track how many actions were requested per beat

def updateScore(data, targets, currentScore): # 
    if (len(data) != len(targets)):
        print("data {} and target {} length mismatch!".format(len(data), len(targets)))
        return
    cp = 0
    ca = 0
    wr = 0
    wn = 0
    tt = 0

    for i in range(len(data)):
        if (len(data[i]) != len(targets[i])):
            print("data {} and target {} inner length mismatch on index {}!".format(len(data[i]), len(targets[i]),i))
            return
        for j in range(len(data[i])):
            if (targets[i][j] == True and data[i][j] == True): #needed action, did action
                ca += 1
                tt += 1
            if (targets[i][j] == True and data[i][j] == False): # needed action, no action (eg was late or missed it)
                wn += 1
                tt += 1
            if (targets[i][j] == False and data[i][j] == True): # no required action, did action (eg failed to remove)
                wr += 1
            if (targets[i][j] == False and data[i][j] == False): # no required action, did no action (eg most of the table inputs)
                cp += 1
    correct_active.append(ca)
    wrong_noAct.append(wn)
    wrong_removal.append(wr)
    correct_passive.append(cp)
    totalTests.append(tt)

    if (sum(totalTests) == 0):
        with open(logFn, 'a', encoding="utf=8") as f:
            f.write("Total tests = 0 \n")
        with open(scoreFn, 'a', encoding="utf=8") as f:
            f.write(str(currentScore) + '\n')
        return currentScore
    score = (3*sum(correct_active) - sum(wrong_removal)) / (3*sum(totalTests))
    if (score >= currentScore): score = score
    elif (score < currentScore): score = fallGain*(score-currentScore) + currentScore
    if (score < scoreRange[0]): score = scoreRange[0]
    if (score > scoreRange[1]): score = scoreRange[1]
    # if (totalTests < 5): score = math.pow(score, .25) # grade on a curve if total events is low
    # elif (totalTests < 10): score = math.pow(score, .5)
    with open(logFn, 'a', encoding="utf=8") as f:
        f.write(str(score) + ", " + str(sum(correct_active)) + ", "+ str(sum(wrong_removal)) + ", "+ str(sum(wrong_noAct)) + ", "+ str(sum(totalTests)) + '\n')
        f.write(str(data)+"\n")
        f.write(str(targets)+"\n")
        f.write(str(correct_active) + "\n\n")
    with open(scoreFn, 'a', encoding="utf=8") as f:
        f.write(str(score) + '\n')
    return score


#####
## MIDI - from autoPopulate.py
#####
midPath = '/home/pi/Python/switchboard/midi/peewee-finalFINALv2_populated.mid'
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

mout = rtmidi.MidiOut()
ports = mout.get_ports()
print(ports)
mout.open_port(2)

#start puredata patch!
PDclient.send_message("/test",[1-rvb,rvb,lpf,1] )

for msg in m.play():
    if (msg.channel == gameTrack and hasattr(msg,'note')): 
        if msg.note in jackInRange:
            if msg.type == "note_off": # turn off LED if off in lead in/out
                pixels[jackLEDFromNote(msg.note-leadInSkip)] = color['off']
            if msg.type == "note_on": # leadIn controls green ON (including solid green during actual target)
                pixels[jackLEDFromNote(msg.note-leadInSkip)] = color['green']   
        if msg.note in jackOutRange:
            if msg.type == "note_off": # turn off LED if off in lead in/out
                pixels[jackLEDFromNote(msg.note-leadOutSkip)] = color['off']
            if msg.type == "note_on" : # leadOut controls red ON
                pixels[jackLEDFromNote(msg.note-leadOutSkip)] = color['red']
        if msg.note in jackRange:
            if msg.type == "note_on":
                pixels[jackLEDFromNote(msg.note)] = color['green']
                updateTargetsFromNote(msg.note, True)
            if msg.type == "note_off":
                pixels[jackLEDFromNote(msg.note)] = color['off']
                updateTargetsFromNote(msg.note, False)
        if msg.note in switchInRange:
            if msg.type == "note_off": # turn off both LEDs if off in lead in/out
                pixels[switchLEDFromNote(msg.note-leadInSkip,'up')] = color['off']
            if msg.type == "note_on":    # turn on top if on in leadin
                pixels[switchLEDFromNote(msg.note-leadInSkip, 'up')] = color['orange']
        if msg.note in switchOutRange:
            if msg.type == "note_off": # turn off both LEDs if off in lead in/out
                pixels[switchLEDFromNote(msg.note-leadOutSkip,'down')] = color['off']
            if msg.type == "note_on":   # turn on bottom if on in leadout
                pixels[switchLEDFromNote(msg.note-leadOutSkip, 'down')] = color['amber']                
        if msg.note in switchRange:
            if msg.type == "note_off":
                pixels[switchLEDFromNote(msg.note, 'down')] = color['amber'] # turn on bottom when targeting note ends
                pixels[switchLEDFromNote(msg.note, 'up')] = color['off'] # turn off top when targeting note ends
                updateTargetsFromNote(msg.note, False)
            if msg.type == "note_on":
                pixels[switchLEDFromNote(msg.note, 'up')] = color['orange'] # turn on top when targeting note starts
                pixels[switchLEDFromNote(msg.note, 'down')] = color['off'] # turn off bottom when targeting note starts
                updateTargetsFromNote(msg.note, True)
        if msg.note == crankPitch + leadInSkip:
            if msg.type == "note_on":
                ser.write(b'y')
            if msg.type == "note_off":
                ser.write(b'n')
        if msg.note == crankPitch:
            if (msg.type == "note_on" and handCrank == 1):
                updateTargetsFromNote(msg.note, True)
        if msg.note == testPointPitch and msg.type == "note_on":
            inputs = getStructuredGPIO(activeGPIO)
            score = updateScore(inputs, switchTargets, score)
            # print (score)
            updatePuredata(score, gameMode)

    elif (msg.channel == bellTrack and hasattr(msg,'note')):
        
        if msg.note == bellPitch:
            if msg.type == "note_on":
                phone.value = False
            if msg.type == "note_off":
                phone.value = True
        if msg.note == alarmPitch:
            if msg.type == "note_on":
                alarm.value = False
            if msg.type == "note_off":
                alarm.value = True
        if msg.note == hornPitch:
            if msg.type == "note_on":
                honk.value = False
            if msg.type == "note_off":
                honk.value = True
    else:
        mout.send_message(msg.bytes())
    pixels.show()

#####
## Clean up: stop DSP...
#####
PDclient.send_message("/test",[1-rvb,rvb,lpf,2] ) #stop the audio TODO: check this actually happens
#GPIO.cleanup()