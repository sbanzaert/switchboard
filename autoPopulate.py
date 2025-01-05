from miditoolkit.midi import parser as mid_parser
from miditoolkit.midi import containers as ct
import math
from pathlib import Path

## takes MIDI w/ a track named "Game" with notes corresponding to jack and switch targets,
## generates additional notes to drive LED lead-in and -out,
## generates additional tracks to drive bell actuators on table
## switchboard has 30 jacks, 8 switches, 1 hand crank o_O

## "game" MIDI track structure:
## PITCHES
## 0-29 - jack targets
## 30-37 - switch targets
## 38 - hand crank
## n + 40 - lead-in (40-79)
## n + 80 - lead-out (80-119)
## 127 - test points (this sets the time the game actually checks inputs)
##
## VELOCITY (actuator selection)
## 127: telephone bell
## 20: alarm
## 40: car horn
## 60: not used

#define pitch ranges, values, velocities as above
jackRange = range(0,30)
switchRange = range(30, 38)
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


fn = "./midi/peewee-dec20.mid"
p = Path(fn)
fn_out = "./midi/{0}_{1}{2}".format(p.stem, "populated", p.suffix)
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
leadOutCount = 4 # must be even!
crankLeadInOut = 4
# TODO: test leadout for switches especially

if (leadOutCount % 2 == 1):
    print("you screwed up! leadout must be even")
    quit()

print(mid.instruments)
print("....................")

for n in mid.instruments[gameTrack].notes:
    for p in jackRange:
        if (n.pitch == p):
            ## generate bell triggers (bell track)
            pitch = bellPitch          # western electric telephone bell
            start = n.start - leadInCount*quarter - (dottedQuarter + sixteenth)
            stop = start + sixteenth
            note = ct.Note(start=start, end=stop, pitch=pitch, velocity = 127)
            mid.instruments[bellTrack].notes.append(note)
            start = n.start - leadInCount*quarter - (quarter + sixteenth)
            stop = start + (quarter + sixteenth)
            note = ct.Note(start=start, end=stop, pitch=pitch, velocity = 127)
            mid.instruments[bellTrack].notes.append(note) 

            ## generate LED lead in/out (game track)
            for i in range(leadInCount):
                start = n.start - (i+1)*quarter
                stop = start + blinkDuration
                pitch = p + leadInSkip
                note = ct.Note(start = start, end = stop, pitch=pitch, velocity=127)
                mid.instruments[gameTrack].notes.append(note)
            # plus a long sustain which will be overriden by the lead-out, one possible double-off when both release at end of this note
            start = n.start
            stop = n.end
            pitch = p + leadInSkip
            note = ct.Note(start = start, end = stop, pitch=pitch, velocity=127)
            mid.instruments[gameTrack].notes.append(note)
            for i in range(leadOutCount):
                start = n.end - (i+1)*quarter + leadOutCount * quarter / 2 ## center the leadout at the end of tested note
                stop = start + blinkDuration
                pitch = p + leadOutSkip
                note = ct.Note(start = start, end = stop, pitch=pitch, velocity=127)
                mid.instruments[gameTrack].notes.append(note)
    for p in switchRange:
        if (n.pitch == p):
        ## generate car horn trigger
            pitch = hornPitch
            start = n.start - leadInCount*quarter - (quarter+3*sixteenth)
            stop = start + (sixteenth)
            note = ct.Note(start=start, end=stop, pitch=pitch, velocity=127)
            mid.instruments[bellTrack].notes.append(note)
            start = n.start - leadInCount*quarter - (quarter)
            stop = start + (quarter)
            note = ct.Note(start=start, end=stop, pitch=pitch, velocity = 127)
            mid.instruments[bellTrack].notes.append(note)

            ## generate LED lead in/out (game track)
            for i in range(leadInCount):    # leadin will control top LED
                start = n.start - (i+1)*quarter
                stop = start + blinkDuration
                pitch = p + leadInSkip
                note = ct.Note(start = start, end = stop, pitch=pitch, velocity=127)
                mid.instruments[gameTrack].notes.append(note)
            for i in range(leadOutCount):   # leadout: bottom LED
                start = n.end - (i+1)*quarter
                stop = start + blinkDuration
                pitch = p + leadOutSkip
                note = ct.Note(start = start, end = stop, pitch=pitch, velocity=127)
                mid.instruments[gameTrack].notes.append(note)    
            

    if (n.pitch == crankPitch):
        ## generate alarm bell
        pitch = alarmPitch          # fire alarm: 1e+AAAAAAAAAAAAA
        start = n.start - leadInCount*quarter - (3*quarter + sixteenth)
        stop = start + (3*quarter + sixteenth)
        note = ct.Note(start=start, end=stop, pitch=pitch, velocity=127)
        mid.instruments[bellTrack].notes.append(note)   
        ## generate arduino trigger
        start = n.start - crankLeadInOut*quarter
        stop = n.end
        pitch = crankPitch + leadInSkip
        note = ct.Note(start=start, end=stop, pitch=pitch, velocity=127)
        mid.instruments[gameTrack].notes.append(note)
            ## generate actuator triggers
            ## std phone ringer: 1,2,3 (e..a),4, lead-in, target live
            # if(n.velocity == velBell ):
            #     pitch = bellPitch          # western electric telephone bell, default
            #     start = n.start - leadInCount*quarter - (dottedQuarter + sixteenth)
            #     stop = start + sixteenth
            #     note = ct.Note(start=start, end=stop, pitch=pitch, velocity = 127)
            #     mid.instruments[bellTrack].notes.append(note)
            #     start = n.start - leadInCount*quarter - (quarter + sixteenth)
            #     stop = start + (quarter + sixteenth)
            #     note = ct.Note(start=start, end=stop, pitch=pitch, velocity = 127)
            #     mid.instruments[bellTrack].notes.append(note)
            # if(n.velocity == velAlarm):
            #     pitch = alarmPitch          # fire alarm: 1e+AAAAAAAAAAAAA
            #     start = n.start - leadInCount*quarter - (3*quarter + sixteenth)
            #     stop = start + (3*quarter + sixteenth)
            #     note = ct.Note(start=start, end=stop, pitch=pitch, velocity=127)
            #     mid.instruments[bellTrack].notes.append(note)
            # if(n.velocity == velHorn):   
            #     pitch = hornPitch              # Car horn: 1...2...3E..4E+A
            #     start = n.start - leadInCount*quarter - (quarter+3*sixteenth)
            #     stop = start + (sixteenth)
            #     note = ct.Note(start=start, end=stop, pitch=pitch, velocity=127)
            #     mid.instruments[bellTrack].notes.append(note)
            #     start = n.start - leadInCount*quarter - (quarter)
            #     stop = start + (quarter)
            #     note = ct.Note(start=start, end=stop, pitch=pitch, velocity = 127)
            #     mid.instruments[bellTrack].notes.append(note)                              

print(mid.instruments)
print(".............")
## generate "check state" timing track
numChecks = math.floor(mid.max_tick/quarter)
for i in range(numChecks):
    pitch = testPointPitch
    start = quarter*i + targetBeat
    stop = start + targetBeat
    note = ct.Note(start = start, end = stop, pitch=pitch, velocity=127)
    mid.instruments[gameTrack].notes.append(note)
print(mid.instruments)
print("..............")
mid.dump(fn_out)