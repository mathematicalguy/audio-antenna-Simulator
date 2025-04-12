from flask import Blueprint, render_template

main_routes = Blueprint('main', __name__)

@main_routes.route('/analysis')
def analysis():
    """Render the analysis page."""
    return render_template('index.html')

# Note: Upload route is now handled by upload_bp in upload.py