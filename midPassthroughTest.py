import mido
import rtmidi
import time 


from mido import MidiFile


m = MidiFile('/home/pi/Python/switchboard/midi/peeweeswitchtest.mid')

mout = rtmidi.MidiOut()
ports = mout.get_ports()
print(ports)
mout.open_port(2)

for msg in m.play():
    if(msg.channel != 15):
        mout.send_message(msg.bytes())
