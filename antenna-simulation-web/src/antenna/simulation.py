import numpy as np
import pyvista as pv
from scipy.io import wavfile
import librosa
import threading
import queue

class AntennaSimulation:
    def __init__(self, antenna_length=1.0, antenna_radius=0.02, max_current=1.0, min_current=0.1, frequency=1.0):
        self.antenna_length = antenna_length
        self.antenna_radius = antenna_radius
        self.max_current = max_current
        self.min_current = min_current
        self.frequency = frequency
        self.running = True
        self.current_time = 0
        self.audio_data = None
        self.sample_rate = None
        self.duration = 0
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
            self.set_audio_data(self.normalize_audio(audio_data), sample_rate)
        except Exception as e:
            print(f"Error loading audio: {e}")
            raise

    def normalize_audio(self, audio):
        return audio.astype(float) / np.max(np.abs(audio))

    def set_audio_data(self, audio_data, sample_rate):
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.duration = len(audio_data) / sample_rate

    def get_current_amplitude(self):
        if self.audio_data is None:
            return self.max_current
        
        # Get current audio sample based on time
        sample_index = int((self.current_time / self.duration) * len(self.audio_data))
        sample_index = min(sample_index, len(self.audio_data) - 1)
        
        # Map audio amplitude to current range
        amplitude = abs(self.audio_data[sample_index])
        current = self.min_current + (self.max_current - self.min_current) * amplitude
        return current

    def make_antenna(self):
        """Create a 3D model of the antenna"""
        body = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, 1), 
                          radius=self.antenna_radius, height=self.antenna_length)
        base = pv.Cylinder(center=(0, 0, -self.antenna_length/20), direction=(0, 0, 1),
                          radius=self.antenna_radius*3, height=self.antenna_length/10)
        top = pv.Sphere(center=(0, 0, self.antenna_length), radius=self.antenna_radius*1.5)
        return body + base + top

    def calculate_field(self, points):
        """Calculate electromagnetic field at given points"""
        # Get current amplitude based on audio
        current = self.get_current_amplitude()
        
        # Calculate distances from antenna
        distances = np.linalg.norm(points, axis=1)
        
        # Calculate phase based on frequency and time
        phase = 2 * np.pi * (self.frequency * self.current_time - distances/2)
        
        # Calculate field vectors
        field = np.zeros_like(points)
        field[:, 0] = current * np.sin(phase) * points[:, 0] / np.maximum(distances, 0.1)
        field[:, 1] = current * np.sin(phase) * points[:, 1] / np.maximum(distances, 0.1)
        field[:, 2] = current * np.cos(phase) * np.cos(np.arctan2(distances, points[:, 2]))
        
        return field

    def update_scene(self, plotter, mesh, field_points):
        """Update the visualization scene"""
        # Update antenna
        plotter.remove_actor("antenna")
        antenna = self.make_antenna()
        plotter.add_mesh(antenna, color='silver', specular=1.0, smooth_shading=True, name="antenna")
        
        # Update field visualization
        field = self.calculate_field(field_points)
        intensities = np.linalg.norm(field, axis=1)
        
        mesh.point_data["vectors"] = field
        mesh.point_data["intensity"] = intensities
        
        # Update time in visualization
        plotter.add_text(f"Time: {self.current_time:.2f}s", name="time_display",
                        position='upper_right', font_size=12, color='white')
        
        if self.audio_data is not None:
            progress = self.current_time / self.duration
            plotter.add_text(f"Progress: {progress*100:.1f}%", name="progress_display",
                           position='upper_right', font_size=12, color='white')
        
        plotter.render()

    def set_parameters(self, length=None, frequency=None, max_current=None, min_current=None):
        """Update simulation parameters"""
        if length is not None:
            self.antenna_length = length
        if frequency is not None:
            self.frequency = frequency
        if max_current is not None:
            self.max_current = max_current
        if min_current is not None:
            self.min_current = min_current

    def set_time(self, time):
        """Set the current simulation time"""
        self.current_time = max(0, min(time, self.duration))

    def run(self, plotter):
        """Run the antenna simulation"""
        while self.running:
            self.update_scene(plotter)
            # Additional simulation logic can be added here