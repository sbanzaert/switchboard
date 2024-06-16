from __future__ import print_function
import RPi.GPIO as GPIO
import time

import rtmidi
from rtmidi.midiconstants import (ALL_SOUND_OFF, CONTROL_CHANGE,
                                  RESET_ALL_CONTROLLERS)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
outPins = (4, 17, 23, 24, 6, 12, 13, 16)
grPins = (4, 23, 6, 13)
rPins = (17, 24, 12, 16)
inPins = (27, 22, 8, 5)

for i in outPins:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, 0)    


midiout = rtmidi.MidiOut()
print(__doc__)

for portnum, portname in enumerate(midiout.get_ports()):
    print("Port:", portname)

    with midiout.open_port(portnum):
        for channel in range(16):
            midiout.send_message([CONTROL_CHANGE | channel, ALL_SOUND_OFF, 0])
            midiout.send_message([CONTROL_CHANGE | channel, RESET_ALL_CONTROLLERS, 0])
            time.sleep(0.05)

        time.sleep(0.1)