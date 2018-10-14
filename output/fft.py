import matplotlib.pyplot as plt
from scipy.io import wavfile as wav
from scipy.fftpack import rfft
import numpy as np
plt.figure(1)
rate, data = wav.read('long_sine.wav')
#data = data / 32767 + 1
fft_out = rfft(data)
#fft_out = np.abs(fft_out)
plt.plot(fft_out.imag, data)

##rate, data = wav.read('long_sine.wav')
##data = data / 32767.0 + 1
##fft_out = fft(data)
##plt.plot(data, np.abs(fft_out))

plt.show()
