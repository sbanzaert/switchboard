#!/usr/bin/python

import rtmidi
from miditoolkit.midi import parser as mid_parser
import RPi.GPIO as GPIO
import math
import board
import neopixel
from mido import MidiFile

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
jackStart = 0
jackEnd = 30
switchStart = 30
switchEnd = 38
jackRange = range(jackStart,jackEnd)
switchRange = range(switchStart, switchEnd)
crankPitch = 38
leadInSkip = 40
leadOutSkip = 80
testPointPitch = 127
velBell = 127
velAlarm = 20
velHorn = 40
bellPitch = 127
alarmPitch = 20
hornPitch = 40


#####
## GPIO - 4 @ 12V relays, active LOW
#####
honk = digitalio.DigitalInOut(board.D27)
phone = digitalio.DigitalInOut(board.D17)
alarm = digitalio.DigitalInOut(board.D23)
unused = digitalio.DigitalInOut(board.D24)
honk.direction = digitalio.Direction.OUTPUT
phone.direction = digitalio.Direction.OUTPUT
alarm.direction = digitalio.Direction.OUTPUT
unused.direction = digitalio.Direction.OUTPUT
honk.value = True
phone.value= True
alarm.value = True
unused.value = True

#####
## Neopixels - one strand for the whole table
#####
def rToL(a: int,b: int ):
    return list(range(a,b))

n0 = rToL(0,10) + rToL(85,95)[::-1] #segments 1 and 6, left jack panel
n1 = rToL(17,27) + rToL(68,78)[::-1] #segments 2 and 5, center jack panel
n2 = rToL(34,44) + rToL(51,61)[::-1] #segments 3 and 4, right jack panel
n3 = rToL(103,113) # segments 7 & 10, left switch panel, seg 10 currently not built
n4 = rToL(120,130) + rToL(135,145)[::-1] # segments 8 & 9, right switch panel
# actually-wired switches:
panel0 = (0,0,1,1,0,
          1,0,0,1,1)
panel1 = (0,0,1,1,0,
          1,0,0,1,1)
panel2 = (0,0,1,1,0,
          1,0,0,1,1)
panel3 = (0,0,1,1,0,
          1,0,0,1,1) # panels 3 and 4 need to be in format 0a0b0a0b or 0ab00ab0 etc
panel4 = (0,0,1,1,0,
          1,0,0,1,1)

switchPanelLEDskip = 4 # 4 switches per panel, skip ahead 4 spots to get to lower LED

panel0Active = [panel0[i] * n0[i] for i in len(n0)]
panel0Active = [i for i in panel0Active if i != 0]
panel1Active = [panel1[i] * n1[i] for i in len(n1)]
panel1Active = [i for i in panel1Active if i != 0]
panel2Active = [panel2[i] * n2[i] for i in len(n2)]
panel2Active = [i for i in panel2Active if i != 0]
panel3Active = [panel3[i] * n3[i] for i in len(n3)]
panel3Active = [i for i in panel3Active if i != 0]
panel4Active = [panel4[i] * n4[i] for i in len(n4)]
panel4Active = [i for i in panel4Active if i != 0]
panelsActive = (panel0Active, panel1Active, panel2Active, panel3Active, panel4Active)

panels = (nA, nB, nC, nD, nE)

allLights = rToL(0,10) + rToL(17,27) + rToL(34,44) + rToL(51,61) + rToL(68,78) + rToL(85,95) + rToL(103,113) + rToL(120,130) + rToL(135,145)
skips = list(range(10,17)) + list(range(27,34)) + list(range(44,51)) + list(range(61,68)) + list(range(78,85))+list(range(95,103))+list(range(113,120))+list(range(130,135))
pixel_pin = board.D18
num_pixels = 145
ORDER = neopixel.GRB # RGB or GRB, changes addressing but commands are always RGB
color = {'red': (255,0,0), 'green': (0,255,0), 'off': (0,0,0)}

ledState=[]
for i in range(num_pixels):
    ledState.append(color['off'])

def ledFromPanel(panelNo: int, pos: int): # this can access all LEDs on the board
    if (panelNo > 4):return 0
    if (panelNo == 3 and pos > 9): return 0
    if (pos > 19): return 0
    return panels[panelNo][pos]

def ledFromNote(pitch: int):    # can only access LEDs attached to wired switches
    if (pitch in range(jackStart+leadInSkip,jackEnd+leadInSkip)):
        bank = math.floor((pitch-leadInSkip)/10)
        return panelsActive(bank, pitch % 10)
    if (pitch in range(jackStart+leadOutSkip, jackEnd+leadOutSkip)):
        bank = math.floor((pitch-leadOutSkip)/10)
        return panelsActive(bank, pitch % 10)
    if (pitch in range(switchStart+leadInSkip, switchEnd+leadInSkip)):
        bank = math.floor((pitch-leadInSkip)/10)
        return panelsActive(bank, pitch % 10)
    if (pitch in range(switchStart+leadOutSkip, switchEnd+leadOutSkip)):
        bank = math.floor((pitch-leadOutSkip)/10)
        return panelsActive(bank, pitch % 10 + switchPanelLEDskip)
    return 0    

#####
## Game setup
#####
score = 100
gain = 0.5
decayRate = 0.6
# jackState = ["grey", "grey", "grey", "grey"]
# jackNoteCenters = [0, 1, 2, 3]
# jackTargets = [0,0,0,0]

switchTargets=[]
for i in range(16*3):
    switchTargets.append(0)  # start with no goals

def targetFromNote(pitch: int):
    if (pitch in range(jackStart,jackEnd)):
        bank = math.floor((pitch-leadInSkip)/10)
        return bank, pitch % 10
    if (pitch in range(switchStart, switchEnd)):
        bank = math.floor((pitch-leadInSkip)/10)-3
        return bank, 10+ pitch % 10
    return 0,0

#####
## GPIO setup
#####


def getSwitches():
    switches=[]
    for i in range(16*3): # fake inputs for now
        switches.append(i % 2)
    return switches
    


def updateScreen():
    for i in range(len(jackState)):
        GPIO.output(grPins[i], 0)
        GPIO.output(rPins[i], 0)
        if (jackState[i] == "red"):
            GPIO.output(rPins[i], 1)
        if (jackState[i] == "green"):
            GPIO.output(grPins[i], 1)

def updateScore():
    global score
    for i in range(len(jackTargets)):
        if (GPIO.input(inPins[i]) == 0 and jackTargets[i] > 0):
            score += math.floor(jackTargets[i]*10)
        if (GPIO.input(inPins[i]) == 1 and jackTargets[i] < 0):
            score -= math.floor(jackTargets[i]*10)
        if (GPIO.input(inPins[i]) == 0 and jackTargets[i] < 0):
            score += math.floor(jackTargets[i]*10)
        if (GPIO.input(inPins[i]) == 1 and jackTargets[i] > 0):
            score -= math.floor(jackTargets[i]*10)            

mout = rtmidi.MidiOut()
ports = mout.get_ports()
print(ports)
mout.open_port(1)


for msg in m.play():
    if (msg.channel == gameTrack):
        for i in jackRange:
            if (msg.type == "note_off" and msg.note == i + leadOutSkip):
                ledState[ledFromNote(i)] = color['off']
                jackTargets[i] = -1
    elif (msg.channel == bellTrack):
        print("test")
    else:
        mout.send_message(msg.bytes())

    if(msg.channel != gameTrack and msg.channel != bell):
        
    else:
        


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