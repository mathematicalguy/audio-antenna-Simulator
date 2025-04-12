import unittest
from src.antenna.simulation import load_audio, normalize_audio

class TestAntennaSimulation(unittest.TestCase):

    def test_load_audio_wav(self):
        audio_data, sample_rate = load_audio('test.wav')
        self.assertIsNotNone(audio_data)
        self.assertEqual(sample_rate, 44100)

    def test_load_audio_mp3(self):
        audio_data, sample_rate = load_audio('test.mp3')
        self.assertIsNotNone(audio_data)
        self.assertEqual(sample_rate, 44100)

    def test_normalize_audio(self):
        audio = np.array([-1, 0, 1])
        normalized = normalize_audio(audio)
        self.assertTrue(np.all(np.abs(normalized) <= 1))

if __name__ == '__main__':
    unittest.main()