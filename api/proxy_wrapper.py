from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)

# Путь к твоему корневому сертификату
CA_CERT_PATH = os.path.join(os.path.dirname(__file__), '..', 'ca.crt')  # если он лежит в корне проекта

@app.route('/')
def wrap_proxy():
    url = request.args.get('url')
    if not url:
        return "❗ Укажи параметр ?url=http://example.com", 400

    try:
        # Проксируем через локальный MITM-прокси
        resp = requests.request(
            method='GET',
            url=url,
            proxies={
                'http': 'http://127.0.0.1:8080',
                'https': 'http://127.0.0.1:8080',
            },
            allow_redirects=True,
            stream=True,
            timeout=10,
            verify=CA_CERT_PATH  # <-- добавили доверие к нашему сертификату
        )

        # Возвращаем оригинальный ответ клиенту
        return Response(
            resp.content,
            status=resp.status_code,
            headers={k: v for k, v in resp.headers.items() if k.lower() != 'content-encoding'}  # убираем gzip
        )

    except Exception as e:
        return f"❌ Ошибка при проксировании: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
