from tableHelpers import *
import subprocess

# print(rToL(4,7))
# q = ((1,1),(2,2))
# print(returnFirstElement(q))

subprocess.call("echo hello world", shell=True)
subprocess.run(["puredata", "-jack", "-jackname sw", "-nojackconnect", "-outchannels 1", "/home/pi/Python/switchboard/headphones/myfirstpd.pd"])

print("code moved on")