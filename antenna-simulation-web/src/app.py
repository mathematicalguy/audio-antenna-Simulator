from flask import Flask, render_template, request, jsonify, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from server.routes import main_routes

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)
CORS(app)

# Register blueprints
app.register_blueprint(main_routes)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Pass initial empty data for the waveform
    initial_data = {
        'waveform': [0] * 100  # Create array of 100 zeros for blank waveform
    }
    return render_template('index.html', initial_data=initial_data)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Here you would process the audio file and generate the waveform
            # For now, we'll just return a success message
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File is too large'}), 413

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)