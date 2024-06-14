from miditoolkit.midi import parser as mid_parser
from miditoolkit.midi import containers as ct
import mido
import math
from pathlib import Path

## "game" MIDI track structure:
## PITCHES
## 0-19 - socket targets
## 20-29 - switch targets
## n + 30 - lead-in (30-59)
## n + 60 - lead-out (60-89)
## n + 90 - "test points" (90-119) -- not needed, covered below
## 120 - test points
##
## VELOCITY (actuator selection)
## 1, 127: telephone bells
## 20: awoooooga horn
## 40: cowbell
## 60: train whistle?


## Prototype implementation:
## 
##
##
##
##

fn = "../music/peeweeswitchtest3.mid"
p = Path(fn)
fn_out = "{0}_{1}{2}".format(p.stem, "populated", p.suffix)
print(fn_out)

mid = mid_parser.MidiFile(fn)
bells = ct.Instrument(program=124, name="Bells")
mid.instruments.append(bells)

g = (i for i, e in enumerate(mid.instruments) if e.name=="Game")
gameTrack = next(g)
g = (i for i, e in enumerate(mid.instruments) if e.name=="Bells")
bellTrack = next(g)
print(gameTrack)
print(bellTrack)

## define some integer offsets & spacings, all in ticks
quarter = mid.ticks_per_beat
dottedQuarter = math.floor(1.5*quarter)
eighth = math.floor(.5* quarter)
sixteenth = math.floor(.25* quarter)
targetMargin = 0.33 # look for success triplet after target live
targetBeat = math.floor(targetMargin * quarter)


blinkDuration = math.floor(.5 * quarter) # eigth-note per blink
leadInCount = 4 # 4-beat intro
leadOutCount = 4


# create track for actuators - this does not work :(
# bellTrack = mido.MidiTrack()
# bellTrack.append(mido.Message('program_change', program=124, time=0))
# mid.instruments.append(bellTrack)

print(mid.instruments)
print("....................")

for n in mid.instruments[gameTrack].notes:
    for p in range(0, 20):
        if (n.pitch == p):
            ## generate LED lead in/out
            for i in range(leadInCount):
                start = n.start - (i+1)*quarter
                stop = start + blinkDuration
                pitch = p + 30
                note = ct.Note(start = start, end = stop, pitch=pitch, velocity=127)
                mid.instruments[gameTrack].notes.append(note)
            for i in range(leadOutCount):
                start = n.end - (i+1)*quarter
                stop = start + blinkDuration
                pitch = p + 60
                note = ct.Note(start = start, end = stop, pitch=pitch, velocity=127)
                mid.instruments[gameTrack].notes.append(note)
            
            # ## generate "test" track -- covered in a single track below
            # numPoints = math.ceil((n.end - n.start)/quarter)
            # for i in range(numPoints):
            #     start = n.start + targetMargin*quarter + quarter*i
            #     stop = start + targetMargin*quarter
            #     pitch = p + 90
            #     note = ct.Note(start = start, end = stop, pitch=pitch, velocity=127)
            #     mid.instruments[gameTrack].notes.append(note)
                

            ## generate phone ringer and other audio signals
            ## std phone ringer: 1,2,3 (e..a),4, lead-in, target live
            if(n.velocity == 127 or n.velocity == 1):
                if(n.velocity == 127):
                    pitch = 93          # ringer 1
                if(n.velocity == 1):
                    pitch = 98          # ringer 2
                start = n.start - leadInCount*quarter - (dottedQuarter + sixteenth)
                stop = start + sixteenth
                note = ct.Note(start=start, end=stop, pitch=pitch, velocity = 127)
                mid.instruments[bellTrack].notes.append(note)
                start = n.start - leadInCount*quarter - (quarter + sixteenth)
                stop = start + (quarter + sixteenth)
                note = ct.Note(start=start, end=stop, pitch=pitch, velocity = 127)
                mid.instruments[bellTrack].notes.append(note)
            if(n.velocity == 20):
                pitch = 82              # awooooooooga
                start = n.start - leadInCount*quarter - (2*quarter + sixteenth)
                stop = start + (2*quarter + sixteenth)
                note = ct.Note(start=start, end=stop, pitch=pitch, velocity=127)
                mid.instruments[bellTrack].notes.append(note)
            if(n.velocity == 40):
                pitch = 83              # COWBELL
                start = n.start - leadInCount*quarter - (3*quarter)
                stop = start + (2*quarter + eighth)
                note = ct.Note(start=start, end=stop, pitch=pitch, velocity=127)
                mid.instruments[bellTrack].notes.append(note)
            if(n.velocity == 60):
                pitch = 84              # CHOO CHOOOOOOO
                start = n.start - leadInCount*quarter - (3*quarter+eighth)
                stop = start + eighth
                note = ct.Note(start=start, end=stop, pitch=pitch, velocity=127)
                mid.instruments[bellTrack].notes.append(note)
                start = n.start - leadInCount*quarter - (2*quarter + eighth)
                stop = start + (2*quarter + eighth)
                note = ct.Note(start=start, end=stop, pitch=pitch, velocity=127)
                mid.instruments[bellTrack].notes.append(note)                                                

print(mid.instruments)
print(".............")
## generate "check state" timing track
numChecks = math.floor(mid.max_tick/quarter)
for i in range(numChecks):
    pitch = 120
    start = quarter*i + targetBeat
    stop = start + targetBeat
    note = ct.Note(start = start, end = stop, pitch=pitch, velocity=127)
    mid.instruments[gameTrack].notes.append(note)
print(mid.instruments)
print("..............")
mid.dump(fn_out)