# Arquivo: Makefile
# Variáveis de Configuração
PROJECT_NAME = arxiv-scraper
DOCKER_USERNAME = mosmendes

# --------------------
# Comandos de Ambiente e Qualidade (Desenvolvimento Local)
# --------------------

install:
	@echo "Instalando dependências com Poetry..."
	poetry install

pre-commit-install:
	@echo "Instalando hooks do pre-commit..."
	poetry run pre-commit install

lint:
	@echo "Executando Ruff para linting e formatação..."
	# Roda o linter e o formatador
	poetry run ruff check src --fix

run:
	@echo "Executando o Web Scraper..."
	# Executa o módulo principal do scraper
	poetry run python -m $(PROJECT_NAME).scraper

# --------------------
# Comandos de Versionamento (Usando bump2version)
# --------------------

version-patch:
	@echo "Aumentando a versão PATCH..."
	# Ex: 0.1.0 -> 0.1.1
	poetry run bump2version patch --tag --commit

version-minor:
	@echo "Aumentando a versão MINOR..."
	# Ex: 0.1.0 -> 0.2.0
	poetry run bump2version minor --tag --commit

# --------------------
# Comandos Docker e Conteinerização
# --------------------

docker-build:
	@echo "Construindo a imagem Docker..."
	docker build -t $(DOCKER_USERNAME)/$(PROJECT_NAME):latest .

docker-run:
	@echo "Executando o container Docker..."
	# -v: Monta o diretório 'data' local no container para persistir o DuckDB
	docker run -v $$(pwd)/data:/app/data $(DOCKER_USERNAME)/$(PROJECT_NAME):latest

docker-push:
	@echo "Fazendo push da imagem para o Docker Hub..."
	docker push $(DOCKER_USERNAME)/$(PROJECT_NAME):latest