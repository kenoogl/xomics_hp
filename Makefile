.PHONY: help build up down restart ps logs check lint-content clean

DOCKER_DIR := docker
SITE_DIR := site
PUBLIC_DIR := public

help:
	@echo "Available targets:"
	@echo "  make build   - Build static site with Hugo"
	@echo "  make up      - Start Nginx container in detached mode"
	@echo "  make down    - Stop and remove containers"
	@echo "  make restart - Restart containers"
	@echo "  make ps      - Show container status"
	@echo "  make logs    - Tail Nginx container logs"
	@echo "  make check   - Run pre-deploy checks"
	@echo "  make lint-content - Validate content naming/front matter conventions"
	@echo "  make clean   - Remove generated public output"

build:
	cd $(SITE_DIR) && TZ=Asia/Tokyo hugo --destination ../$(PUBLIC_DIR) --cleanDestinationDir

up:
	cd $(DOCKER_DIR) && docker-compose up -d --build

down:
	cd $(DOCKER_DIR) && docker-compose down

restart: down up

ps:
	cd $(DOCKER_DIR) && docker-compose ps

logs:
	cd $(DOCKER_DIR) && docker-compose logs -f --tail=100

lint-content:
	python scripts/validate_content.py

check:
	@test -f $(DOCKER_DIR)/docker-compose.yml || (echo "Missing docker-compose.yml" && exit 1)
	@test -f nginx/nginx.conf || (echo "Missing nginx.conf" && exit 1)
	@test -f $(SITE_DIR)/config.toml || (echo "Missing Hugo config.toml" && exit 1)
	$(MAKE) lint-content
	$(MAKE) build
	@test -f $(PUBLIC_DIR)/index.html || (echo "Missing generated public/index.html" && exit 1)
	@echo "Check passed: config files present and Hugo build succeeded."

clean:
	rm -rf $(PUBLIC_DIR)/*
