from shared_memory_dict import SharedMemoryDict
from time import sleep

outgoing_params = SharedMemoryDict(name='parameters', size=1024)
outgoing_params['reverbWet']=0

while True:
    outgoing_params['reverbWet']=outgoing_params['reverbWet']+10
    if (outgoing_params['reverbWet'] == 100):
        outgoing_params['reverbWet'] = 0
    sleep(2)


    