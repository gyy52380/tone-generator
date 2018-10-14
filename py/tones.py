import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile as wav

'''
CONSTANTS
'''
FREQUENCY = 44100


def generate_tone_with_attack_decay(tone_frequency_hz, duration_s, attack_duration_s, decay_duration_s, frequency = FREQUENCY, silence_padding_left_s=0, silence_padding_right_s=0):
    sample_count = int(duration_s * frequency)
    dt = 1 / frequency

    samples = np.zeros(sample_count)

    #attack multiplier array
    attack_sample_count = int(attack_duration_s * frequency)
    attack_multiplier_array = -np.logspace(-1, 1, num=attack_sample_count)[::-1] / 10 + 1.01 #looks good!

    #decay multiplier array
    decay_sample_count = int(decay_duration_s * frequency)
    decay_multiplier_array = -np.logspace(-1, 1, num=decay_sample_count) / 10 + 1.01 #looks good!

    for i in range(sample_count):
        t = dt * i

        base_amplitude = np.sin(2*np.pi * tone_frequency_hz * t)

        if i < attack_sample_count:
            base_amplitude *= attack_multiplier_array[i]
        elif i >= sample_count - decay_sample_count:
            idx = i - (sample_count - decay_sample_count)
            base_amplitude *= decay_multiplier_array[idx]

        samples[i] = base_amplitude
        
    samples_i16 = np.int16(samples * 32767)

    #pad with silence
    silent_samples_left_count = int(silence_padding_left_s * frequency)
    silent_samples_right_count = int(silence_padding_right_s * frequency)

    samples_i16 = np.concatenate((np.zeros(silent_samples_left_count, dtype=np.int16)+1, samples_i16, np.zeros(silent_samples_right_count, dtype=np.int16)+1))
        
    return samples_i16


def graph_fft_in_same_window(list_of_samples, frequency=FREQUENCY):

    for i in range(len(list_of_samples)):
        samples = list_of_samples[i]

        #normalise to [0, 1]
        samples = np.float64(samples) / 32767
        samples = (samples + 1.0) / 2

        #get fourier transform and correct indicies in Hz
        fft = np.fft.fft(samples)
        fft_length = len(fft)
        fftfreq = np.fft.fftfreq(fft_length, d=1/frequency) #to show frequency in Hz

        #get plot axis in correct units
        x = fftfreq[:fft_length//2]
        y = np.abs(fft[:fft_length//2])
        
        #plot
        #plt.figure(i)
        plt.xlabel("[Hz]")
        plt.plot(x, y)

    plt.legend(["duži ton", "kraći ton"])
    plt.show()

def graph_fft_in_separate_window(list_of_samples, frequency=FREQUENCY):

    for i in range(len(list_of_samples)):
        samples = list_of_samples[i]

        #normalise to [0, 1]
        samples = np.float64(samples) / 32767
        samples = (samples + 1.0) / 2

        #get fourier transform and correct indicies in Hz
        fft = np.fft.fft(samples)
        fft_length = len(fft)
        fftfreq = np.fft.fftfreq(fft_length, d=1/frequency) #to show frequency in Hz

        #get plot axis in correct units
        x = fftfreq[:fft_length//2]
        y = np.abs(fft[:fft_length//2])
        
        #plot
        plt.xlabel("[Hz]")
        plt.figure(i)
        plt.plot(x, y)

    #plt.legend(['o'*(i+1) for i in range(len(list_of_samples))])
    plt.show()


############################################################################
############################################################################

wavs = {}
wave_graph_audacity_f = 1024

wavs["tone_long_220_fake"] = generate_tone_with_attack_decay(220, 1.5, 0.5, 0.5, wave_graph_audacity_f, 0.1, 0.1) #for a nice wave graph in audacity, lower freq and shorter
wavs["tone_long_220"] = generate_tone_with_attack_decay(220, 3, 0.5, 0.5, FREQUENCY, 0.2, 0.2)
wavs["tone_long_210"] = generate_tone_with_attack_decay(210, 3, 0.5, 0.5, FREQUENCY, 0.2, 0.2)
wavs["tone_long_230"] = generate_tone_with_attack_decay(230, 3, 0.5, 0.5, FREQUENCY, 0.2, 0.2)
wavs["long_tones_combined"] = np.concatenate((wavs["tone_long_210"], wavs["tone_long_220"], wavs["tone_long_230"]))

wavs["tone_short_220_fake"] = generate_tone_with_attack_decay(220, 0.5, 0.1, 0.1, wave_graph_audacity_f, 0.1, 0.1)
wavs["tone_short_220"] = generate_tone_with_attack_decay(220, 0.1, 0.05, 0.05, FREQUENCY, 0.1, 0.1)
wavs["tone_short_210"] = generate_tone_with_attack_decay(210, 0.1, 0.05, 0.05, FREQUENCY, 0.1, 0.1)
wavs["tone_short_230"] = generate_tone_with_attack_decay(230, 0.1, 0.05, 0.05, FREQUENCY, 0.1, 0.1)
wavs["short_tones_combined"] = np.concatenate((wavs["tone_short_210"], wavs["tone_short_220"], wavs["tone_short_230"]))

for key, value in wavs.items():
    wav.write(key+".wav", FREQUENCY, value)


graphing_frequency = 2048

tone_long_for_graph= generate_tone_with_attack_decay(220, 3, 0.5, 0.5, graphing_frequency, 0.1, 0.1)
tone_short_for_graph = generate_tone_with_attack_decay(220, 0.1, 0.05, 0.05, graphing_frequency, 0.1, 0.1)

plt.xlabel("[Hz]")
graph_fft_in_separate_window((tone_long_for_graph, tone_short_for_graph), graphing_frequency)
graph_fft_in_same_window((tone_long_for_graph, tone_short_for_graph), graphing_frequency)

wave_graph_f = 1024

