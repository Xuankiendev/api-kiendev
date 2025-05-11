from flask import Flask
import datetime
from setup import setup_app

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
request_logs = []
start_time = datetime.datetime.now()

setup_app(app)

if __name__ == '__main__':
    app.run(debug=True)
