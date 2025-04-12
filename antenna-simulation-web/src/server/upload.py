from flask import Blueprint, request, jsonify, current_app
import os
import numpy as np
import matplotlib.pyplot as plt
import librosa
import io
import base64
import traceback
from werkzeug.utils import secure_filename
from antenna.simulation import AntennaSimulation

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_audio(file_path):
    """Process audio file and return normalized data"""
    try:
        # Load and normalize audio
        audio_data, sample_rate = librosa.load(file_path, sr=None)
        duration = len(audio_data) / sample_rate
        
        # Normalize audio to [-1, 1] range
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        return audio_data, sample_rate, duration
    except Exception as e:
        current_app.logger.error(f"Error processing audio: {str(e)}")
        raise

def create_waveform_plot(audio_data, sample_rate):
    """Create visualization of the audio waveform"""
    plt.figure(figsize=(10, 4))
    plt.plot(np.arange(len(audio_data)) / sample_rate, audio_data)
    plt.title('Audio Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    
    # Convert plot to base64 image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()

def upload_file():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                try:
                    # Process audio file
                    audio_data, sample_rate, duration = process_audio(file_path)
                    
                    # Create waveform visualization
                    waveform_plot = create_waveform_plot(audio_data, sample_rate)
                    
                    # Initialize antenna simulation
                    simulation = AntennaSimulation()
                    simulation.set_audio_data(audio_data, sample_rate)
                    
                    return jsonify({
                        'message': 'File uploaded successfully',
                        'filename': filename,
                        'audioPlot': waveform_plot,
                        'audioData': audio_data.tolist(),
                        'duration': duration,
                        'sampleRate': sample_rate,
                        'initialParameters': {
                            'antennaLength': simulation.antenna_length,
                            'frequency': simulation.frequency,
                            'maxCurrent': simulation.max_current,
                            'minCurrent': simulation.min_current
                        }
                    }), 200
                    
                except Exception as e:
                    current_app.logger.error(f"Error processing file: {str(e)}")
                    current_app.logger.error(f"Traceback: {traceback.format_exc()}")
                    return jsonify({'error': f'Error processing file: {str(e)}'}), 500
                finally:
                    # Clean up the uploaded file
                    if os.path.exists(file_path):
                        os.remove(file_path)
            except Exception as e:
                current_app.logger.error(f"Error saving file: {str(e)}")
                return jsonify({'error': f'Error saving file: {str(e)}'}), 500
        
        return jsonify({'error': 'File type not allowed'}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload():
    return upload_file()

@upload_bp.route('/update-parameters', methods=['POST'])
def update_parameters():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Update simulation parameters
        simulation = AntennaSimulation()
        simulation.set_parameters(
            length=data.get('antennaLength'),
            frequency=data.get('frequency'),
            max_current=data.get('maxCurrent'),
            min_current=data.get('minCurrent')
        )
        
        return jsonify({'success': True}), 200
    except Exception as e:
        current_app.logger.error(f"Error updating parameters: {str(e)}")
        return jsonify({'error': str(e)}), 500