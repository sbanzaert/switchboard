import mido
import rtmidi
import time 
import pygame

from mido import MidiFile
jackState = ["grey", "grey", "grey", "grey","grey", "grey", "grey", "grey"]
jackNoteCenters = [71, 74, 77, 80, 83, 86, 89, 92]

m = MidiFile('../music/peeweeswitchtest.mid ')

mout = rtmidi.MidiOut()
ports = mout.get_ports()
print(ports)
mout.open_port(0)

pygame.init()
screen = pygame.display.set_mode((960,540))
screen.fill("black")

def updateScreen():
    for i in range(len(jackState)):
        pygame.draw.circle(screen, jackState[i], (100*i+80,80),20)
    pygame.display.flip()

print(m.type)

updateScreen()

for msg in m.play():
    if(msg.channel != 15):
        mout.send_message(msg.bytes())
    else:
        #print(msg)
        for i in range(len(jackState)):
            if (msg.type== "note_off" and (jackNoteCenters[i]-1<= msg.note <= jackNoteCenters[i]+1)):
                jackState[i] = "grey"
            elif (msg.type == "note_on" and msg.note == jackNoteCenters[i]+1):
                jackState[i] = "orange"
            elif (msg.type == "note_on" and msg.note == jackNoteCenters[i]):
                jackState[i] = "green"
            elif (msg.type == "note_on" and msg.note == jackNoteCenters[i]-1):
                jackState[i] = "red"
        updateScreen()
