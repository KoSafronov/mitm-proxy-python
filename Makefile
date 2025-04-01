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

.PHONY: gen-cert
gen-cert:
	@if not exist certs mkdir certs
	openssl genrsa -out ca.key 2048
	openssl req -new -x509 -days 3650 -key ca.key -out ca.crt -subj "/CN=proxy CA"
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
