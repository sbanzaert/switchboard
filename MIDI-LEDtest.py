import mido
import rtmidi
from miditoolkit.midi import parser as mid_parser
import RPi.GPIO as GPIO
import tkinter as tk

from mido import MidiFile
midPath = '/home/pi/Projects/switchboard/peeweeswitchtest3_populated.mid'
m=MidiFile(midPath)
midParsed = mid_parser.MidiFile(midPath)
g = (i for i, e in enumerate(midParsed.instruments) if e.name=="Game")
gameTrack = next(g) + 1
checkNote = 120
score = 100

root = tk.Tk()
root.geometry("{0}x{1}+0+0".format(int(root.winfo_screenwidth()/2), int(root.winfo_screenheight()/2)))
l = tk.Label(text=score, fg='red',font=('Helvetica', 120))
l.pack(expand=True)
root.update()

jackState = ["grey", "grey", "grey", "grey"]
jackNoteCenters = [0, 1, 2, 3]
jackTargets = [0,0,0,0] # 0 = nop, 1 = actuated

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
outPins = (4, 17, 23, 24, 6, 12, 13, 16)
grPins = (4, 23, 6, 13)
rPins = (17, 24, 12, 16)
inPins = (27, 22, 8, 5)

for i in outPins:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, 0)    

for i in inPins:
    GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
        if (GPIO.input(inPins[i]) == jackTargets[i]):
            score += 1
        else:
            score -= 1
    l.config(text=score)
    root.update()

mout = rtmidi.MidiOut()
ports = mout.get_ports()
print(ports)
mout.open_port(1)


for msg in m.play():
    if(msg.channel != gameTrack):
        mout.send_message(msg.bytes())
    else:
        for i in range(len(jackState)):
            if (msg.type == "note_off" and msg.note == jackNoteCenters[i]):
                jackState[i] = "grey"
                jackTargets[i] = 1
            elif (msg.type == "note_off" and msg.note == jackNoteCenters[i]+30):
                jackState[i] = 'grey'
            elif (msg.type == "note_off" and  msg.note == jackNoteCenters[i]+60):
                jackState[i] = 'grey'   
            elif (msg.type == "note_on" and msg.note == jackNoteCenters[i]+60):
                jackState[i] = "red"
            elif (msg.type == "note_on" and msg.note == jackNoteCenters[i]+30):
                jackState[i] = "green"
            elif (msg.type == "note_on" and msg.note == jackNoteCenters[i]):
                jackState[i] = "green"
                jackTargets[i] = 0
        if (msg.type == "note_on" and msg.note == checkNote):
            updateScore()
        updateScreen()
GPIO.cleanup()