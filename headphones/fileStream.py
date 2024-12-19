from pedalboard import Pedalboard, Chorus, LowpassFilter, Bitcrush
# likely plugins: chorus, reverb, lowpass, bitcrush
from pedalboard.io import AudioFile, AudioStream

with AudioStream(
    input_device_name=AudioStream.input_device_names[0],
    output_device_name=AudioStream.output_device_names[0],
    allow_feedback=True,
    buffer_size=128,
    sample_rate=44100
) as stream:
    stream.plugins = Pedalboard([
        Bitcrush(bit_depth=16),
        LowpassFilter(cutoff_frequency_hz=400),
        Chorus(),  
    ])
    input("Press enter to stop")
