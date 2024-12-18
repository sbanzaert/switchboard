from time import sleep
import board
import digitalio

honk = digitalio.DigitalInOut(board.D4)
phone = digitalio.DigitalInOut(board.D17)
alarm = digitalio.DigitalInOut(board.D23)
unused = digitalio.DigitalInOut(board.D24)
honk.direction = digitalio.Direction.OUTPUT
phone.direction = digitalio.Direction.OUTPUT
alarm.direction = digitalio.Direction.OUTPUT
unused.direction = digitalio.Direction.OUTPUT
honk.value = True
phone.value= True
alarm.value = True
unused.value = True

while True:
    honk.value = False
    sleep(.5)
    honk.value = True
    sleep(2)
    phone.value = False
    sleep(.5)
    phone.value = True
    sleep(2)
    alarm.value = False
    sleep(.5)
    alarm.value = True
    sleep(2)