from time import sleep
import board
import digitalio

## in relay order: header is GND 1 2 3 4 +5V
alarm = digitalio.DigitalInOut(board.D23) 
unused = digitalio.DigitalInOut(board.D24)
phone = digitalio.DigitalInOut(board.D25)
honk = digitalio.DigitalInOut(board.D8)


honk.direction = digitalio.Direction.OUTPUT
phone.direction = digitalio.Direction.OUTPUT
alarm.direction = digitalio.Direction.OUTPUT
unused.direction = digitalio.Direction.OUTPUT
honk.value = True
phone.value= True
alarm.value = True
unused.value = True

while True:
    # honk.value = False
    # sleep(.5)
    # honk.value = True
    # sleep(2)
    phone.value = False
    sleep(.2)
    phone.value = True
    sleep(.15)
    phone.value = False
    sleep(1.5)
    phone.value = True
    sleep(.4)

    # alarm.value = False
    # sleep(.5)
    # alarm.value = True
    # sleep(2)