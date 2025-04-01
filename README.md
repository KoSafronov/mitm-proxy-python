<<<<<<< HEAD

# mitm-proxy-python

# MITM Proxy — это перехватывающий HTTP/HTTPS прокси-сервер, написанный на Python.

# MITM Proxy Python

**MITM Proxy** — это перехватывающий HTTP/HTTPS прокси-сервер, написанный на Python.

Он позволяет:

- 🔄 Проксировать и логировать HTTP и HTTPS-запросы
- 📜 Повторно отправлять и анализировать перехваченные запросы через веб-интерфейс
- 🔍 Выполнять базовый анализ уязвимостей (XSS, SQLi)

---

## 🚀 Запуск проекта

### 1. Генерация корневого сертификат

```bash
make gen-cert
```

Создаются:

- `ca.key` — приватный ключ CA
- `ca.crt` — публичный корневой сертификат
- `cert.key` — ключ, на базе которого подписываются поддельные host-сертификаты

### 2. Сборка и запуск Docker

```bash
make docker-build
make docker-start
```

Прокси слушает:

- `http://localhost:8080` — HTTP/HTTPS прокси
- `http://localhost:8000` — REST API

### 3. Установка сертификата CA в систему (Windows):

```powershell
certutil -addstore -f "Root" ca.crt
```

Для Linux/macOS — открой `ca.crt` и импортируй в системное хранилище.

### 4. Проверка:

```bash
curl -x http://127.0.0.1:8080 http://example.com
curl -x http://127.0.0.1:8080 https://mail.ru -v --ssl-no-revoke --tlsv1.2
```

---

## Возможности

### Проксирование HTTP(S)

- Прокси перехватывает и обрабатывает все типы HTTP-запросов (GET, POST, PUT, OPTIONS и др)
- Поддержка TLS MITM: сертификаты генерируются "на лету" под каждый домен

### REST API (порт 8000)

| Метод | Путь             | Описание                   |
| ----- | ---------------- | -------------------------- |
| GET   | `/requests`      | Список всех запросов       |
| GET   | `/requests/<id>` | Подробности одного запроса |
| POST  | `/repeat/<id>`   | Повторить отправку запроса |
| POST  | `/scan/<id>`     | Выполнить базовый анализ   |

---

## Остановка и очистка

```bash
make docker-stop     # Остановить контейнер
make clean-certs     # Удалить временные сертификаты
```

---

## 🛑 Ограничения

- ❌ Не используются внешние прокси-библиотеки (например, `mitmproxy`, `proxy.py`)
- ✅ Всё реализовано с использованием стандартных Python-библиотек и `openssl`

---

Проект выполнен в рамках учебного задания — VK Edu
MITM-прокси с REST-интерфейсом. Пригоден для анализа трафика и изучения принципов работы HTTPS.

> > > > > > > 2134d0f (Initial commit)
