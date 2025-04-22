DOCKER_COMPOSE=docker/docker-compose.yaml

.PHONY: docker-build
docker-build:
	docker compose -f $(DOCKER_COMPOSE) build

.PHONY: docker-start
docker-start:
	docker compose -f $(DOCKER_COMPOSE) up -d

.PHONY: docker-stop
docker-stop:
	docker compose -f $(DOCKER_COMPOSE) down

.PHONY: docker-up
docker-up:
	docker compose -f $(DOCKER_COMPOSE) up -d
	@echo "⏳ Ждём запуск PostgreSQL..."
	@timeout 10 > NUL || sleep 10
	@docker exec mitm-proxy-python python init_db.py || echo "⚠️ Ошибка инициализации БД"

.PHONY: gen-cert
gen-cert:
	@if [ ! -d certs ]; then mkdir certs; fi
	openssl genrsa -out ca.key 2048
	openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
		-out ca.crt -config docker/openssl.cnf
	openssl genrsa -out cert.key 2048


.PHONY: gen-host-cert
gen-host-cert:
	@if [ -z "$$host" ]; then echo "Usage: make gen-host-cert host=example.com"; exit 1; fi
	@serial=$$(date +%s); \
	openssl req -new -key cert.key -subj "/CN=$$host" -sha256 | \
	openssl x509 -req -days 3650 -CA ca.crt -CAkey ca.key -set_serial $$serial -out certs/$$host.crt

.PHONY: clean-certs
clean-certs:
	rm -rf certs *.crt *.key temp.csr

.PHONY: init-db
init-db:
	python init_db.py
