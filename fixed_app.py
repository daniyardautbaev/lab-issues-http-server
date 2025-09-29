# fixed_app.py
from flask import Flask, request, jsonify
import json
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
SECRET_API_KEY = os.getenv('SECRET_API_KEY', 'not-set')

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception("Unhandled exception")
    return jsonify({"error": "Internal server error"}), 500

@app.route('/unsafe-deserialize', methods=['POST'])
def safe_deserialize():
    data = request.get_json(silent=True)
    if not data or 'payload' not in data:
        return jsonify({"error": "Bad request"}), 400
    payload = data.get('payload')
    try:
        obj = json.loads(payload) if isinstance(payload, str) else payload
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400
    if isinstance(obj, dict) and obj.get('action') in ('ping', 'status'):
        return jsonify({"result": "ok", "action": obj.get('action')})
    return jsonify({"error": "Unsupported payload"}), 400

@app.route('/show-secret')
def show_secret():
    return jsonify({"status": "ok", "secret_set": bool(SECRET_API_KEY and SECRET_API_KEY != 'not-set')})

@app.route('/cause-error')
def cause_error():
    raise RuntimeError("Demo error for testing")
    return "ok"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
