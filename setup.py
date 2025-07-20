import os
import importlib
from flask import Flask, jsonify, request
import requests
import datetime

totalRequests = 0
startTime = datetime.datetime.now()

def create_app():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False

    apis_dir = os.path.join(os.path.dirname(__file__), 'apis')
    for filename in os.listdir(apis_dir):
        if filename.endswith('.py') and not filename.startswith('_'):
            module_name = f"apis.{filename[:-3]}"
            module = importlib.import_module(module_name)
            for attr in dir(module):
                obj = getattr(module, attr)
                if hasattr(obj, 'register_blueprint'):
                    continue
                if hasattr(obj, 'register_blueprint'):
                    continue
                if hasattr(obj, 'register') or hasattr(obj, 'name'):
                    try:
                        app.register_blueprint(obj)
                    except Exception:
                        pass

    @app.before_request
    def increment_requests():
        global totalRequests
        totalRequests += 1

    @app.route('/stats')
    def stats():
        uptime = datetime.datetime.now() - startTime
        return jsonify({
            "totalRequests": totalRequests,
            "uptimeSeconds": int(uptime.total_seconds())
        })

    return app

def send_request(url, method='GET', params=None, json_data=None, headers=None, timeout=10):
    method = method.upper()
    try:
        if method == 'GET':
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
        elif method == 'POST':
            r = requests.post(url, params=params, json=json_data, headers=headers, timeout=timeout)
        else:
            r = requests.request(method, url, params=params, json=json_data, headers=headers, timeout=timeout)
        return r.status_code, r.text
    except requests.RequestException as e:
        return None, str(e)
