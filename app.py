from flask import Flask, request, jsonify, send_from_directory
import json
import os
from typing import Union, Dict

# Define the app with the correct static folder
app = Flask(__name__, static_url_path='', static_folder='ui')

# Path to the configuration file
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config', 'config.json')

# Default configuration settings
DEFAULT_CONFIG = {
    'chat_rules': [
        "Be respectful.",
        "No hate speech, harassment, or discrimination.",
        "No spamming or inappropriate content."
    ],
    'warnings_before_ban': 3
}

# Load or initialize configuration
def load_config() -> Dict[str, Union[str, int, list]]:
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_CONFIG

# Save configuration to file with explicit type hinting for file object
def save_config(configuration: Dict[str, Union[str, int, list]]) -> Union[None, Dict[str, str]]:
    try:
        # Use type hinting to define the file object type
        with open(CONFIG_FILE, 'w') as f:  # 'f' is a TextIO object supporting write(str)
            json.dump(configuration, f, indent=4)
    except Exception as e:
        return {"error": f"Failed to save configuration: {str(e)}"}

# Global configuration variable
current_config = load_config()

# Serve index.html from the ui folder as the homepage
@app.route('/')
def home():
    # Serve the index.html from the ui directory
    return send_from_directory(app.static_folder, 'index.html')

# Configuration route
@app.route('/config', methods=['GET', 'POST'])
def config_route():
    global current_config
    if request.method == 'POST':
        new_config = request.json
        save_result = save_config(new_config)
        if "error" in save_result:
            return jsonify(save_result), 500
        current_config = new_config  # Update the global config with the new values
        return jsonify({"message": "Configuration updated!"}), 200

    return jsonify(current_config), 200

# Serve other static files like CSS and JS from the ui directory
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

# Route for testing server
@app.route('/test')
def test():
    return "Server is running and this endpoint is accessible!"

if __name__ == '__main__':
    # Ensure the config directory exists
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

    # Run the Flask application
    app.run(host='0.0.0.0', port=5000)
