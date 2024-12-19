from pythonosc.udp_client import SimpleUDPClient
from time import sleep
ip = '127.0.0.1'
port = 1337

client = SimpleUDPClient(ip,port)
rvb = 0
lpf = 4000

while True:
    print("{}, {}, {}".format(1-rvb,rvb,lpf))
    client.send_message("/test",[1-rvb,rvb,lpf] )
    sleep(1)
    rvb = rvb + .02
    lpf = lpf - 300
    if rvb == 1: rvb = 0
    if lpf == 80: lpf = 80

