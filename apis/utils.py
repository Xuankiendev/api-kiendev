from flask import Response, request
import json
import os
from datetime import datetime
from pymongo import MongoClient

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

def log_request():
    log_data = {
        'ip': request.remote_addr,
        'endpoint': request.path,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    try:
        mongo_uri = os.getenv('MONGODB_URI')
        if not mongo_uri:
            log_data['error'] = 'Chưa có MONGODB_URI'
            return
        
        client = MongoClient(mongo_uri)
        db = client['api_logs']
        collection = db['requests']
        collection.insert_one(log_data)
        client.close()
        
    except Exception as e:
        error_log = {
            'ip': request.remote_addr,
            'endpoint': request.path,
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }
        try:
            if mongo_uri:
                client = MongoClient(mongo_uri)
                db = client['api_logs']
                collection = db['requests']
                collection.insert_one(error_log)
                client.close()
        except:
            pass
