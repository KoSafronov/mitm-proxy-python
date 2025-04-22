from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/')
def proxy_wrapper():
    url = request.args.get('url')
    if not url:
        return "No URL provided", 400

    try:
        resp = requests.get(url, proxies={'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}, stream=True)
        return Response(resp.raw, status=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(port=8888)
