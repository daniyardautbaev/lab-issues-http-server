# vulnerable_app.py
from flask import Flask, request, jsonify
import json
import traceback

app = Flask(__name__)

# Хардкод секрет в коде (умышленно уязвимо)
SECRET_API_KEY = "MY_SUPER_SECRET_API_KEY_12345"

# Конфигурационный файл (закоммичен) - example config.json
# Пример небезопасной десериализации - имитация: позволяю клиенту прислать "action" который выполняется
@app.route('/unsafe-deserialize', methods=['POST'])
def unsafe_deserialize():
    # Предположим, клиент присылает JSON с полем "payload" в виде строки JSON
    body = request.get_data(as_text=True)
    # Уязвимость: использование eval/unsafe loader (здесь имитируем небезопасную обработку)
    data = json.loads(body)
    payload = data.get('payload')
    # Небезопасная "десериализация": допустим кто-то прислал: {"cmd": "os.system('rm -rf /')"} - это иллюстрация
    # (в реальном коде не использовать eval; здесь только учебный пример)
    try:
        obj = eval(payload)  # ОПАСНО — НИКОГДА ТАК НЕ ДЕЛАЙТЕ
        return jsonify({"result": str(obj)})
    except Exception as e:
        # Возвращаем стек-трейс пользователю — это демонстрирует утечку внутренней информации
        return f"Error occurred:\n{traceback.format_exc()}", 500

@app.route('/show-secret')
def show_secret():
    # Эндпоинт который демонстрирует, что секрет есть в коде
    return f"API KEY: {SECRET_API_KEY}"

@app.route('/cause-error')
def cause_error():
    # Просто вызов ошибки с трассировкой
    1/0  # вызовет ZeroDivisionError и покажет traceback в режиме debug
    return "ok"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
