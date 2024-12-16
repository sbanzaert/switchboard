from time import sleep
import board
import digitalio

honk = digitalio.DigitalInOut(board.D18)
honk.direction = digitalio.Direction.OUTPUT

while True:
    honk.value = False
    sleep(1)
    honk.value = True
    sleep(2)