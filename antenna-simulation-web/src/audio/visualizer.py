import numpy as np
import matplotlib.pyplot as plt

class AudioVisualizer:
    def __init__(self, audio_data, sample_rate):
        self.audio_data = audio_data
        self.sample_rate = sample_rate

    def plot_waveform(self):
        plt.figure(figsize=(10, 4))
        plt.plot(self.audio_data, color='blue')
        plt.title('Audio Waveform')
        plt.xlabel('Samples')
        plt.ylabel('Amplitude')
        plt.grid()
        plt.show()

    def plot_spectrum(self):
        spectrum = np.fft.fft(self.audio_data)
        freqs = np.fft.fftfreq(len(spectrum), 1/self.sample_rate)
        magnitude = np.abs(spectrum)

        plt.figure(figsize=(10, 4))
        plt.plot(freqs[:len(freqs)//2], magnitude[:len(magnitude)//2], color='red')
        plt.title('Audio Spectrum')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')
        plt.grid()
        plt.show()