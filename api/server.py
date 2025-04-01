from flask import Flask, jsonify, request
from app import storage, scanner
import requests

app = Flask(__name__)

@app.route("/requests", methods=["GET"])
def list_requests():
    return jsonify(storage.get_all_requests())

@app.route("/requests/<req_id>", methods=["GET"])
def get_request(req_id):
    req = storage.get_request_by_id(req_id)
    if not req:
        return jsonify({"error": "Not found"}), 404
    return jsonify(req)

@app.route("/repeat/<req_id>", methods=["POST"])
def repeat_request(req_id):
    req = storage.get_request_by_id(req_id)
    if not req:
        return jsonify({"error": "Not found"}), 404
    try:
        r = requests.request(req['method'], req['url'], headers=req['headers'])
        return jsonify({"status_code": r.status_code, "response": r.text[:500]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/scan/<req_id>", methods=["POST"])
def scan_request(req_id):
    req = storage.get_request_by_id(req_id)
    if not req:
        return jsonify({"error": "Not found"}), 404
    result = scanner.scan_request(req)
    return jsonify({"scan_result": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
