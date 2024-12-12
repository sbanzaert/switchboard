#!/usr/bin/python

# from https://spotify.github.io/pedalboard/faq.html
# to do: output stream to alsa


from pedalboard import Pedalboard, Chorus, Reverb
# likely plugins: chorus, reverb, lowpass, bitcrush
from pedalboard.io import AudioFile
from tqdm import tqdm

board = Pedalboard([Chorus(), Reverb()])
reverb = board[1]

# Smaller step sizes would give a smoother transition,
# at the expense of processing speed
step_size_in_samples = 100

# Manually step through the audio _n_ samples at a time, reading in chunks:
with AudioFile("untitled.wav") as af:

    # Open the output audio file so that we can directly write audio as we process, saving memory:
    with AudioFile(
        "sample-processed-output.wav", "w", af.samplerate, num_channels=af.num_channels
    ) as o:

        # Create a progress bar to show processing speed in real-time:
        with tqdm(total=af.frames, unit=' samples') as pbar:
            for i in range(0, af.frames, step_size_in_samples):
                chunk = af.read(step_size_in_samples)

                # Set the reverb's "wet" parameter to be equal to the
                # percentage through the track (i.e.: make a ramp from 0% to 100%)
                percentage_through_track = i / af.frames
                reverb.wet_level = percentage_through_track

                # Update our progress bar with the number of samples received:
                pbar.update(chunk.shape[1])

                # Process this chunk of audio, setting `reset` to `False`
                # to ensure that reverb tails aren't cut off
                output = board.process(chunk, af.samplerate, reset=False)
                o.write(output)

