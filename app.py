from flask import Flask, render_template, Response
import json
import os
from importlib import import_module
import glob

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        VALID_API_KEYS = {config['apikey']: "active"}
except (FileNotFoundError, json.JSONDecodeError):
    VALID_API_KEYS = {os.getenv('API_KEY', 'xuankien1212'): "active"}

def validate_api_key(api_key):
    if not api_key:
        return {"error": "Thiếu ApiKey", "status_code": 401}
    if api_key not in VALID_API_KEYS:
        return {"error": "ApiKey không hợp lệ", "status_code": 401}
    status = VALID_API_KEYS[api_key]
    if status == "inactive":
        return {"error": "ApiKey đã bị thay đổi", "status_code": 403}
    if status == "banned":
        return {"error": "ApiKey đã bị cấm", "status_code": 403}
    return {"valid": True}

def load_media(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

api_dir = os.path.join(os.path.dirname(__file__), 'apis')
for file in glob.glob(os.path.join(api_dir, '*.py')):
    if not file.endswith('__init__.py'):
        module_name = os.path.splitext(os.path.basename(file))[0]
        module = import_module(f'apis.{module_name}')
        if hasattr(module, 'bp'):
            app.register_blueprint(module.bp)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
