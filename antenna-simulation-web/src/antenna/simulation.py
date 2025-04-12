import numpy as np
import pyvista as pv
from scipy.io import wavfile
import librosa
import threading
import queue

class AntennaSimulation:
    def __init__(self, antenna_length=1.0, antenna_radius=0.02):
        self.antenna_length = antenna_length
        self.antenna_radius = antenna_radius
        self.running = True
        self.audio_lock = threading.Lock()
        self.message_queue = queue.Queue()

    def load_audio(self, filename):
        """Load audio from either WAV or MP3 files"""
        try:
            if filename.lower().endswith('.mp3'):
                audio_data, sample_rate = librosa.load(filename, sr=None)
            else:
                sample_rate, audio_data = wavfile.read(filename)
                if len(audio_data.shape) > 1:
                    audio_data = np.mean(audio_data, axis=1)  # Convert stereo to mono
            return self.normalize_audio(audio_data), sample_rate
        except Exception as e:
            print(f"Error loading audio: {e}")
            raise

    def normalize_audio(self, audio):
        return audio.astype(float) / np.max(np.abs(audio))

    def make_antenna(self):
        """Create a 3D model of the antenna"""
        body = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, 1), 
                           radius=self.antenna_radius, height=self.antenna_length)
        base = pv.Cylinder(center=(0, 0, -self.antenna_length/20), direction=(0, 0, 1),
                           radius=self.antenna_radius*3, height=self.antenna_length/10)
        top = pv.Sphere(center=(0, 0, self.antenna_length), radius=self.antenna_radius*1.5)
        return body + base + top

    def update_scene(self, plotter):
        """Update the visualization scene"""
        plotter.remove_actor("antenna")
        antenna_actor = plotter.add_mesh(self.make_antenna(), 
                                          color='silver', 
                                          specular=1.0,
                                          smooth_shading=True,
                                          name="antenna")
        plotter.render()

    def run(self, plotter):
        """Run the antenna simulation"""
        while self.running:
            self.update_scene(plotter)
            # Additional simulation logic can be added here