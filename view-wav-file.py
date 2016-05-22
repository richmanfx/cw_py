#!/usr/bin/python
from matplotlib import pyplot as plt
import numpy as np
import wave
import sys

spf = wave.open('dot.wav', 'r')

# Extract Raw Audio from Wav File
signal = spf.readframes(-1)
signal = np.fromstring(signal, 'Int16')


# If Stereo
if spf.getnchannels() == 2:
    print 'Just mono files'
    sys.exit(0)

plt.figure(1)
plt.title('Signal Wave')
plt.xlabel("Time")
plt.ylabel("Amplitude")
# plt.plot(signal[0:4096])
plt.plot(signal)
plt.show()
