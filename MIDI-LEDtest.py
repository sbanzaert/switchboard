import mido
import rtmidi
import RPi.GPIO as GPIO
from mido import MidiFile

m=MidiFile('/home/pi/Projects/MIDIsynth/peeweeswitchtest.mid')

jackState = ["grey", "grey", "grey", "grey"]
jackNoteCenters = [71, 74, 77, 80]

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
outPins = (4, 17, 23, 24, 6, 12, 13, 16)
grPins = (4, 23, 6, 13)
rPins = (17, 24, 12, 16)

for i in outPins:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, 0)    

def updateScreen():
    for i in range(len(jackState)):
        GPIO.output(grPins[i], 0)
        GPIO.output(rPins[i], 0)
        if (jackState[i] == "red"):
            GPIO.output(rPins[i], 1)
        if (jackState[i] == "green"):
            GPIO.output(grPins[i], 1)
    
mout = rtmidi.MidiOut()
ports = mout.get_ports()
print(ports)
mout.open_port(1)

for msg in m.play():
    if(msg.channel != 15):
        mout.send_message(msg.bytes())
    else:
        for i in range(len(jackState)):
            if (msg.type== "note_off" and (jackNoteCenters[i]-1<= msg.note <= jackNoteCenters[i]+1)):
                jackState[i] = "grey"
            elif (msg.type == "note_on" and msg.note == jackNoteCenters[i]+1):
                jackState[i] = "red"
            elif (msg.type == "note_on" and msg.note == jackNoteCenters[i]):
                jackState[i] = "green"
            elif (msg.type == "note_on" and msg.note == jackNoteCenters[i]-1):
                jackState[i] = "red"
        updateScreen()
GPIO.cleanup()