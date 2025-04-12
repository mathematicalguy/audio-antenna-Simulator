# filepath: /antenna-simulation-web/antenna-simulation-web/src/server/routes.py
from flask import Blueprint
from .upload import upload_file

main_routes = Blueprint('main', __name__)

@main_routes.route('/upload', methods=['POST'])
def upload():
    return upload_file()