import psycopg2
import json

DB_CONFIG = {
    'dbname': 'mitm_proxy',
    'user': 'postgres',
    'password': '1234',
    'host': 'db',  # Важно: имя сервиса из docker-compose
    'port': 5432
}

def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS http_requests (
            id TEXT PRIMARY KEY,
            method TEXT,
            path TEXT,
            get_params JSONB,
            headers JSONB,
            cookies JSONB,
            post_params JSONB,
            response_code INTEGER,
            response_message TEXT,
            response_headers JSONB,
            response_body TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def store_request(req_id, data):
    print(f"[+] Сохраняем запрос {req_id}")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO http_requests (
            id, method, path, get_params, headers, cookies, post_params,
            response_code, response_message, response_headers, response_body
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    ''', (
        req_id,
        data['method'],
        data['path'],
        json.dumps(data.get('get_params', {})),
        json.dumps(data.get('headers', {})),
        json.dumps(data.get('cookies', {})),
        json.dumps(data.get('post_params', {})),
        data.get('response_code'),
        data.get('response_message'),
        json.dumps(data.get('response_headers', {})),
        data.get('response_body')
    ))
    conn.commit()
    cur.close()
    conn.close()

def get_all_requests():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT id, method, path FROM http_requests")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {row[0]: {"method": row[1], "path": row[2]} for row in rows}

def get_parsed_request_by_id(req_id):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT * FROM http_requests WHERE id = %s", (req_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "method": row[1],
        "path": row[2],
        "get_params": json.loads(row[3]),
        "headers": json.loads(row[4]),
        "cookies": json.loads(row[5]),
        "post_params": json.loads(row[6]),
        "response_code": row[7],
        "response_message": row[8],
        "response_headers": json.loads(row[9]),
        "response_body": row[10]
    }
