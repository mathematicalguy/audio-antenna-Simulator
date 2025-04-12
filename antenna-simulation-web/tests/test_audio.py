# filepath: /antenna-simulation-web/antenna-simulation-web/tests/test_audio.py
import unittest
from src.audio.processor import load_audio
from src.audio.visualizer import create_audio_plot

class TestAudioProcessing(unittest.TestCase):

    def test_load_audio_wav(self):
        audio_data, sample_rate = load_audio('test_audio.wav')
        self.assertIsNotNone(audio_data)
        self.assertEqual(sample_rate, 44100)  # Assuming the test file has a sample rate of 44100 Hz

    def test_load_audio_mp3(self):
        audio_data, sample_rate = load_audio('test_audio.mp3')
        self.assertIsNotNone(audio_data)
        self.assertEqual(sample_rate, 44100)  # Assuming the test file has a sample rate of 44100 Hz

    def test_create_audio_plot(self):
        audio_data = [0.1, 0.2, 0.3, 0.4, 0.5]  # Sample audio data
        plot = create_audio_plot(audio_data)
        self.assertIsNotNone(plot)  # Ensure that a plot is created

if __name__ == '__main__':
    unittest.main()