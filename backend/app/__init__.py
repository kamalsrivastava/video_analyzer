from flask import Flask
import os
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configuration
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mp3', 'wav'}
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from .routes.upload import upload_blueprint
    app.register_blueprint(upload_blueprint)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5000)
