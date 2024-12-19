#!/usr/bin/python
# windows 10 requires pedalboard v0.9.6 or below  :|
from pedalboard import Pedalboard, Chorus, Bitcrush, LowpassFilter
# likely plugins: chorus, reverb, lowpass, bitcrush
from pedalboard.io import AudioFile, AudioStream
# from shared_memory_dict import SharedMemoryDict
# incoming_params = SharedMemoryDict(name='parameters', size=1024)
board = Pedalboard([Bitcrush(), LowpassFilter(), Chorus()])
reverb = board[1]

# Smaller step sizes would give a smoother transition,
# at the expense of processing speed
step_size_in_samples = 100

with AudioFile("./audio/untitled.wav") as af:
    chunk = af.read(af.samplerate * 10)
with AudioStream(sample_rate=af.samplerate, output_device_name="USB Audio Device; USB Stream Output", num_output_channels=2) as s:
    s.play(chunk)

# Manually step through the audio _n_ samples at a time, reading in chunks:
# with AudioFile("./audio/untitled.wav") as af:
    
#     with AudioStream(
#         input_device_name=AudioStream.input_device_names[0],
#         output_device_name=AudioStream.output_device_names[-1],
#         allow_feedback=True,
#         buffer_size=128,
#         sample_rate=44100,
#         num_input_channels=1,
#         num_output_channels=2
#     ) as stream:
#         stream.plugins = Pedalboard([
#             Bitcrush(bit_depth=16),
#             LowpassFilter(cutoff_frequency_hz=800),
#             Chorus(),  
#         ])
#         for i in range(0, af.frames, step_size_in_samples):
#                 chunk = af.read(step_size_in_samples)

#                 # Set the reverb's "wet" parameter to be equal to the
#                 # percentage through the track (i.e.: make a ramp from 0% to 100%)
#                 percentage_through_track = i / af.frames
#                 #reverb.wet_level = percentage_through_track
#                 reverb.wet_level = incoming_params['reverbWet']
#                 print(reverb.wet_level)
#                 AudioStream.write(chunk, af.samplerate)

                

