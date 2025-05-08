from flask import Blueprint, request
import tempfile
import os
from gtts import gTTS
from .utils import check_key, json_response

text_to_audio_bp = Blueprint('text_to_audio', __name__)

@text_to_audio_bp.route('/text_to_audio', methods=['GET'])
def text_to_audio():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    text = request.args.get('text', '')
    if not text:
        return json_response({'error': 'Cần văn bản', 'status': 400}, 400)

    try:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            audio_file = temp_file.name
        tts = gTTS(text=text, lang='vi')
        tts.save(audio_file)
        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        return Response(audio_data, mimetype='audio/mpeg')
    except Exception as e:
        return json_response({'error': f'Lỗi chuyển giọng: {str(e)}', 'status': 500}, 500)
    finally:
        if 'audio_file' in locals() and os.path.exists(audio_file):
            os.remove(audio_file)
