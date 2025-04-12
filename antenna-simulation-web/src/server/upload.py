from flask import Blueprint, request, jsonify
import os
import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import librosa
import io
import base64
import traceback
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configure PyVista for off-screen rendering
pv.OFF_SCREEN = True
pv.global_theme.background = 'black'
pv.global_theme.window_size = [800, 400]
pv.global_theme.anti_aliasing = 'msaa'  # Changed from True to 'msaa'

class AntennaVisualizer:
    def __init__(self, audio_data, sample_rate):
        print("Initializing AntennaVisualizer...")
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.pl = None
        try:
            self.pl = pv.Plotter(off_screen=True)
            print("PyVista plotter created successfully")
            self.setup_scene()
        except Exception as e:
            print(f"Error creating plotter: {str(e)}")
            print(traceback.format_exc())
            raise
        
    def setup_scene(self):
        print("Setting up visualization scene...")
        try:
            self.pl.window_size = [800, 400]
            self.pl.set_background('black')
            self.pl.enable_eye_dome_lighting()
            
            # Create antenna
            self.create_antenna()
            
            # Set up camera for interactive view
            self.pl.camera_position = 'iso'
            self.pl.camera.zoom(1.5)
            print("Scene setup complete")
        except Exception as e:
            print(f"Error in setup_scene: {str(e)}")
            print(traceback.format_exc())
            raise
        
    def create_antenna(self):
        print("Creating antenna model...")
        try:
            antenna_length = 1.0
            antenna_radius = 0.02
            
            body = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, 1), 
                              radius=antenna_radius, height=antenna_length)
            base = pv.Cylinder(center=(0, 0, -antenna_length/20), direction=(0, 0, 1),
                              radius=antenna_radius*3, height=antenna_length/10)
            top = pv.Sphere(center=(0, 0, antenna_length), radius=antenna_radius*1.5)
            
            antenna = body + base + top
            self.pl.add_mesh(antenna, color='silver', specular=1.0, smooth_shading=True)
            print("Antenna model created successfully")
        except Exception as e:
            print(f"Error creating antenna: {str(e)}")
            print(traceback.format_exc())
            raise
        
    def update_field(self, audio_chunk):
        try:
            # Generate field points in a spherical pattern
            phi = np.linspace(0, 2*np.pi, 30)
            theta = np.linspace(0, np.pi, 15)
            r = np.linspace(0.2, 2.0, 10)
            
            points = []
            for ri in r:
                for ti in theta:
                    for pi in phi:
                        x = ri * np.sin(ti) * np.cos(pi)
                        y = ri * np.sin(ti) * np.sin(pi)
                        z = ri * np.cos(ti)
                        points.append([x, y, z])
            
            points = np.array(points)
            
            # Normalize audio chunk
            normalized_audio = audio_chunk / np.max(np.abs(audio_chunk))
            
            # Create field vectors modulated by audio
            vectors = points * np.interp(
                np.linalg.norm(points, axis=1),
                [0, np.max(np.linalg.norm(points, axis=1))],
                [1, 0]
            )[:, np.newaxis]
            
            # Modulate vectors with audio data
            for i in range(len(vectors)):
                vectors[i] *= normalized_audio[i % len(normalized_audio)]
            
            # Create field visualization
            field_data = pv.PolyData(points)
            field_data["vectors"] = vectors
            
            # Update field visualization
            self.pl.remove_actor("field")
            self.pl.add_mesh(field_data.glyph(orient="vectors", scale="vectors", factor=0.1),
                            name="field", cmap="plasma", opacity=0.7)
        except Exception as e:
            print(f"Error updating field: {str(e)}")
            print(traceback.format_exc())
            raise
    
    def generate_frames(self, num_frames=30):
        print(f"Generating {num_frames} frames...")
        frames = []
        try:
            chunk_size = len(self.audio_data) // num_frames
            
            for i in range(num_frames):
                print(f"Processing frame {i+1}/{num_frames}")
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size
                audio_chunk = self.audio_data[start_idx:end_idx]
                
                # Update field for this chunk
                self.update_field(audio_chunk)
                
                # Render and capture frame
                self.pl.render()
                frame = self.pl.screenshot(transparent_background=True)
                
                # Convert frame to base64
                frame_buffer = io.BytesIO()
                plt.imsave(frame_buffer, frame, format='png')
                frame_buffer.seek(0)
                frames.append(base64.b64encode(frame_buffer.getvalue()).decode())
            
            print("Frame generation complete")
            return frames
        except Exception as e:
            print(f"Error generating frames: {str(e)}")
            print(traceback.format_exc())
            raise

def upload_file():
    try:
        print("\n=== Upload Request Debug Info ===")
        print("Request Method:", request.method)
        print("Request Files:", request.files)
        print("Request Form:", request.form)
        print("Content Type:", request.content_type)

        if 'audio' not in request.files:
            print("No audio file in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['audio']
        if file.filename == '':
            print("No filename")
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                print(f"Saving file to: {file_path}")
                file.save(file_path)
                print("File saved successfully")
                
                try:
                    print("Loading audio data...")
                    # Load audio data
                    audio_data, sample_rate = librosa.load(file_path, sr=None)
                    print(f"Audio loaded: {len(audio_data)} samples, {sample_rate}Hz")
                    
                    print("Creating visualization...")
                    # Create visualization frames
                    visualizer = AntennaVisualizer(audio_data, sample_rate)
                    frames = visualizer.generate_frames()
                    print(f"Generated {len(frames)} frames")
                    
                    print("Creating waveform plot...")
                    # Create audio waveform plot
                    plt.figure(figsize=(10, 4))
                    plt.plot(np.arange(len(audio_data)) / sample_rate, audio_data)
                    plt.title('Audio Waveform')
                    plt.xlabel('Time (s)')
                    plt.ylabel('Amplitude')
                    plt.grid(True)
                    
                    # Convert audio plot to base64
                    audio_buffer = io.BytesIO()
                    plt.savefig(audio_buffer, format='png', bbox_inches='tight')
                    audio_buffer.seek(0)
                    plt.close()
                    
                    print("Sending response...")
                    return jsonify({
                        'message': 'File uploaded successfully',
                        'filename': filename,
                        'audioPlot': base64.b64encode(audio_buffer.getvalue()).decode(),
                        'visualizationFrames': frames,
                        'duration': len(audio_data) / sample_rate
                    }), 200
                    
                except Exception as e:
                    print(f"Error processing file: {str(e)}")
                    print("Traceback:", traceback.format_exc())
                    return jsonify({'error': f'Error processing file: {str(e)}'}), 500
                finally:
                    # Clean up the uploaded file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print("Temporary file cleaned up")
            except Exception as e:
                print(f"Error saving file: {str(e)}")
                print("Traceback:", traceback.format_exc())
                return jsonify({'error': f'Error saving file: {str(e)}'}), 500
        
        print("File type not allowed")
        return jsonify({'error': 'File type not allowed'}), 400
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print("Traceback:", traceback.format_exc())
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload():
    return upload_file()