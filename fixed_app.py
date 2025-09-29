# fixed_app.py
from flask import Flask, request, jsonify
import json
import os
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

app = Flask(__name__)

# Читаем секрет из .env вместо хардкода
SECRET_API_KEY = os.getenv("SECRET_API_KEY", "not-set")

# Логирование ошибок в файл
logging.basicConfig(filename='app.log', level=logging.INFO)

# Глобальный обработчик ошибок (не показываем traceback пользователю)
@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception("Unhandled exception occurred")
    return jsonify({"error": "Internal server error"}), 500

@app.route('/safe-deserialize', methods=['POST'])
def safe_deserialize():
    """
    Безопасная десериализация:
    - Парсим JSON
    - Проверяем допустимую структуру
    - Никаких eval!
    """
    data = request.get_json(silent=True)
    if not data or 'payload' not in data:
        return jsonify({"error": "Bad request"}), 400

    payload = data.get('payload')

    try:
        obj = json.loads(payload) if isinstance(payload, str) else payload
        # Разрешаем только простые действия
        if isinstance(obj, dict) and obj.get('action') in ('ping', 'status'):
            return jsonify({"result": "ok", "action": obj.get('action')})
        else:
            return jsonify({"error": "Unsupported payload"}), 400
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400

@app.route('/show-secret')
def show_secret():
    """
    Вместо возврата секрета — показываем только, установлен ли он
    """
    return jsonify({
        "status": "ok",
        "secret_set": SECRET_API_KEY != "not-set"
    })

@app.route('/health')
def health():
    return jsonify({"status": "running"})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)
