from flask import Flask, render_template
from apis.check_ban import check_ban_bp
from apis.zingmp3 import zingmp3_bp
from apis.random_media import random_media_bp
from apis.tiktok import tiktok_bp
from apis.gemini import gemini_bp
from apis.screenshot import screenshot_bp
from apis.text_to_audio import text_to_audio_bp

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

for bp in [check_ban_bp, zingmp3_bp, random_media_bp, tiktok_bp, gemini_bp, screenshot_bp, text_to_audio_bp]:
    app.register_blueprint(bp)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
