from flask import Response
import json
import os

with open('config.json', 'r') as f:
    API_KEYS = json.load(f).get('API_KEYS', {'xuankien1212': 'active'})

def check_key(api_key):
    if not api_key:
        return {'error': 'Thiếu API Key', 'status': 401}
    if api_key not in API_KEYS:
        return {'error': 'API Key sai', 'status': 401}
    return None

def json_response(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False),
        mimetype='application/json',
        status=status
    )
