from flask import Blueprint, request, jsonify
import os
import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import librosa
import io
import base64
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

# Configure PyVista for off-screen rendering
pv.OFF_SCREEN = True

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_antenna_visualization(audio_data):
    # Create off-screen plotter
    pl = pv.Plotter(off_screen=True)
    pl.window_size = [800, 600]
    
    # Create antenna geometry
    antenna_length = 1.0
    antenna_radius = 0.02
    
    # Create antenna components
    cylinder = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, 1), 
                         radius=antenna_radius, height=antenna_length)
    base = pv.Cylinder(center=(0, 0, -0.05), direction=(0, 0, 1),
                      radius=antenna_radius*2, height=0.1)
    
    # Add components to plotter
    pl.add_mesh(cylinder, color='silver', smooth_shading=True)
    pl.add_mesh(base, color='darkgray', smooth_shading=True)
    
    # Create electromagnetic field visualization
    audio_chunk = audio_data[:1000]  # Use first 1000 samples
    normalized_audio = audio_chunk / np.max(np.abs(audio_chunk))
    
    # Generate field points
    theta = np.linspace(0, 2*np.pi, 20)
    phi = np.linspace(0, np.pi, 10)
    r = np.linspace(0.1, 1, 5)
    
    points = []
    for ri in r:
        for ti in theta:
            for pi in phi:
                x = ri * np.sin(pi) * np.cos(ti)
                y = ri * np.sin(pi) * np.sin(ti)
                z = ri * np.cos(pi)
                points.append([x, y, z])
    
    points = np.array(points)
    
    # Create field vectors
    vectors = points * np.interp(
        np.linalg.norm(points, axis=1),
        [0, np.max(np.linalg.norm(points, axis=1))],
        [1, 0]
    )[:, np.newaxis]
    
    # Modulate vectors with audio data
    for i in range(len(vectors)):
        vectors[i] *= normalized_audio[i % len(normalized_audio)]
    
    # Add vectors to visualization
    arrows = pv.PolyData(points)
    arrows["vectors"] = vectors
    pl.add_mesh(arrows.glyph(orient="vectors", scale="vectors", factor=0.1),
               cmap="plasma", opacity=0.7)
    
    # Set camera position and lighting
    pl.camera_position = 'iso'
    pl.camera.zoom(1.5)
    
    # Render to image
    image = pl.screenshot()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.imsave(buffer, image, format='png')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()

def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        try:
            # Load audio data
            audio_data, sample_rate = librosa.load(file_path)
            
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
            
            # Create antenna visualization
            antenna_plot = create_antenna_visualization(audio_data)
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'audioPlot': base64.b64encode(audio_buffer.getvalue()).decode(),
                'antennaPlot': antenna_plot
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload():
    return upload_file()