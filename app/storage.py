requests_db = {}


def store_request(req_id, data):
    requests_db[req_id] = data

def get_all_requests():
    return requests_db

def get_request_by_id(req_id):
    return requests_db.get(req_id)

def store_request(req_id, data):
    print(f"[+] Сохраняем запрос {req_id}")
    requests_db[req_id] = data
