from flask import Blueprint, request
import requests
import json
from .utils import check_key, json_response

gemini_bp = Blueprint('gemini', __name__)

@gemini_bp.route('/chat_gemini', methods=['GET'])
def chat_gemini():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    ask = request.args.get('ask', '')
    if not ask:
        return json_response({'error': 'Cần câu hỏi', 'status': 400}, 400)

    prompt = request.args.get('prompt', '')
    try:
        api_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=AIzaSyC5VvVGBk3T0TzfF_JCaDTDPAW97oRhdrc'
        data = {
            'contents': [{'role': 'user', 'parts': [{'text': prompt or ask}]}]
        }
        response = requests.post(api_url, headers={'Content-Type': 'application/json'}, data=json.dumps(data), timeout=5)
        if response.status_code != 200:
            return json_response({'error': 'Lỗi API Gemini', 'status': 500}, 500)

        result = response.json()
        if 'candidates' not in result or not result['candidates']:
            return json_response({'error': 'Không có trả lời từ Gemini', 'status': 500}, 500)

        answer = result['candidates'][0]['content']['parts'][0]['text']
        return json_response({
            'query': ask,
            'answer': answer,
            'prompt': prompt or 'Không có prompt'
        })
    except Exception as e:
        return json_response({'error': f'Lỗi server: {str(e)}', 'status': 500}, 500)
