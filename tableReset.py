import digitalio
import board
alarm = digitalio.DigitalInOut(board.D23) 
unused = digitalio.DigitalInOut(board.D24)
phone = digitalio.DigitalInOut(board.D25)
honk = digitalio.DigitalInOut(board.D8)
crankA = digitalio.DigitalInOut(board.D21) ## CHOSEN AT RANDOM, FIX IN PERSON
crankB = digitalio.DigitalInOut(board.D22)
for io in (honk, phone, alarm, unused, crankA, crankB):
    io.direction = digitalio.Direction.INPUT
    
