COMPOSE=docker compose

.PHONY: help build up down logs ps migrate backend-shell worker test clean

help:
	@echo "Targets:"
	@echo "  make build          Build backend and frontend images"
	@echo "  make up             Start db, backend and frontend"
	@echo "  make worker         Start Telegram worker profile"
	@echo "  make down           Stop containers"
	@echo "  make logs           Follow logs"
	@echo "  make ps             Show containers"
	@echo "  make migrate        Run Alembic migrations"
	@echo "  make backend-shell  Open shell in backend container"
	@echo "  make test           Run pytest in backend container"
	@echo "  make clean          Stop containers and remove volumes"

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d db backend frontend

worker:
	$(COMPOSE) --profile worker up worker

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

migrate:
	$(COMPOSE) run --rm backend python -m alembic upgrade head

backend-shell:
	$(COMPOSE) run --rm backend sh

test:
	$(COMPOSE) run --rm backend python -m pytest

clean:
	$(COMPOSE) down -v
