import numpy as np
import librosa

def load_audio(filename):
    """Load audio from either WAV or MP3 files."""
    try:
        if filename.lower().endswith('.mp3'):
            audio_data, sample_rate = librosa.load(filename, sr=None)
        else:
            audio_data, sample_rate = librosa.load(filename, sr=None)
        return normalize_audio(audio_data), sample_rate
    except Exception as e:
        print(f"Error loading audio: {e}")
        raise

def normalize_audio(audio):
    """Normalize audio data to the range [-1, 1]."""
    return audio.astype(float) / np.max(np.abs(audio))