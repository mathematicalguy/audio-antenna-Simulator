from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from server.routes import main_routes
from server.upload import upload_bp
import pyvista as pv

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)

# Add more detailed CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}
app.config['UPLOAD_FOLDER'] = os.path.abspath(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure PyVista for off-screen rendering
pv.OFF_SCREEN = True

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register blueprints
app.register_blueprint(main_routes)
app.register_blueprint(upload_bp)  # Register the upload blueprint

@app.route('/')
def index():
    """Render the index page."""
    initial_data = {
        'waveform': [0] * 100  # Create array of 100 zeros for blank waveform
    }
    return render_template('index.html', initial_data=initial_data)

@app.errorhandler(413)
def too_large(e):
    """Handle file size errors."""
    return jsonify({'error': 'File is too large'}), 413

@app.errorhandler(500)
def server_error(e):
    """Handle internal server error."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)