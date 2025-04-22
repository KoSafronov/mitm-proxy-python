
import socket
import threading
import uuid
from urllib.parse import urlparse, parse_qs
import requests
import ssl
import subprocess
import os
import time
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from app import storage
from http.cookies import SimpleCookie

CERTS_DIR = "certs"
CA_CERT = "ca.crt"
CA_KEY = "ca.key"
CERT_KEY = "cert.key"

os.makedirs(CERTS_DIR, exist_ok=True)

class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = BytesIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()
        self.body = self.rfile.read()  # Читаем тело запроса

def generate_cert(hostname):
    cert_path = os.path.join(CERTS_DIR, f"{hostname}.crt")
    key_path = CERT_KEY

    if not os.path.exists(cert_path):
        print(f"[cert] Генерация сертификата для {hostname}")
        serial = int(time.time())

        with open("temp.csr", "wb") as csr_file:
            subprocess.run([
                "openssl", "req", "-new", "-key", key_path, "-subj", f"/CN={hostname}", "-sha256"
            ], stdout=csr_file, check=True)

        subprocess.run([
            "openssl", "x509", "-req", "-days", "3650", "-in", "temp.csr",
            "-CA", CA_CERT, "-CAkey", CA_KEY, "-set_serial", str(serial), "-out", cert_path
        ], check=True)

        print(f"[cert] Сертификат создан: {cert_path}")

    return cert_path, key_path

def handle_https_tunnel(client_socket, host, port):
    try:
        print(f"[https] Обрабатываю CONNECT {host}:{port}")

        cert_path, key_path = generate_cert(host)
        client_socket.sendall(b"HTTP/1.0 200 Connection established\r\n\r\n")

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        ssl_client = context.wrap_socket(client_socket, server_side=True)

        print(f"[ssl] Подключаемся к {host}:{port} по TLS")
        raw_server = socket.create_connection((host, port))
        ssl_server = ssl.create_default_context().wrap_socket(raw_server, server_hostname=host)

        def forward(source, target):
            try:
                while True:
                    data = source.recv(4096)
                    if not data:
                        break
                    target.sendall(data)
            except Exception as e:
                print(f"[forward] Ошибка: {e}")

        t1 = threading.Thread(target=forward, args=(ssl_client, ssl_server))
        t2 = threading.Thread(target=forward, args=(ssl_server, ssl_client))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    except Exception as e:
        print(f"[https tunnel] Ошибка: {e}")
    finally:
        client_socket.close()

def parse_request_details(request, body):
    parsed_url = urlparse(request.path if request.path.startswith("http") else f"http://{request.headers['Host']}{request.path}")
    headers = dict(request.headers)
    headers.pop('Proxy-Connection', None)

    # Куки
    cookies = {}
    if 'Cookie' in headers:
        cookie = SimpleCookie()
        cookie.load(headers['Cookie'])
        cookies = {k: v.value for k, v in cookie.items()}

    # GET параметры
    get_params = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed_url.query).items()}

    # POST параметры
    post_params = {}
    if headers.get("Content-Type", "").startswith("application/x-www-form-urlencoded"):
        post_params = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(body.decode(errors='ignore')).items()}

    return parsed_url, headers, cookies, get_params, post_params

def handle_client(client_socket):
    try:
        request_data = client_socket.recv(65536)
        if not request_data:
            return

        request = HTTPRequest(request_data)

        if request.command == "CONNECT":
            target_host, target_port = request.path.split(":")
            handle_https_tunnel(client_socket, target_host, int(target_port))
            return

        req_id = str(uuid.uuid4())
        method = request.command
        parsed_url, headers, cookies, get_params, post_params = parse_request_details(request, request.body)
        url = parsed_url.geturl()
        path = parsed_url.path

        try:
            resp = requests.request(method, url, headers=headers, data=request.body, stream=True, allow_redirects=False)
        except Exception as e:
            print("[proxy] Ошибка при отправке запроса:", e)
            return

        # Ответ
        response_body = resp.content
        response_headers = dict(resp.headers)
        response_code = resp.status_code
        response_message = resp.reason

        if response_body is None:
            response_body = b""
            
        print(f"[debug] req_id: {req_id}")
        print(f"[debug] full URL: {url}")
        print(f"[debug] Method: {method}, Headers: {headers}, Body: {request.body}")



        storage.store_request(req_id, {
            "method": method,
            "path": path,
            "get_params": get_params,
            "headers": headers,
            "cookies": cookies,
            "post_params": post_params,
            "response_code": response_code,
            "response_message": response_message,
            "response_headers": response_headers,
            "response_body": response_body.decode("utf-8", errors="ignore")[:10000]
        })


        # Отправить клиенту
        response_text = f"HTTP/1.1 {response_code} {response_message}\r\n"
        for k, v in resp.headers.items():
            response_text += f"{k}: {v}\r\n"
        response_text += '\r\n'
        client_socket.sendall(response_text.encode())

        for chunk in resp.iter_content(chunk_size=4096):
            if chunk:
                client_socket.sendall(chunk)

    except Exception as e:
        print("[proxy] General error:", e)
    finally:
        client_socket.close()

def start_proxy():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 8080))
    server.listen(100)
    print("[*] Proxy listening on port 8080")

    while True:
        client_sock, _ = server.accept()
        threading.Thread(target=handle_client, args=(client_sock,)).start()

if __name__ == "__main__":
    start_proxy()
