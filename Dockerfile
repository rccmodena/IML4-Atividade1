# Arquivo: Dockerfile

# ----------------------------------------
# STAGE 1: BUILD - Instala dependências com Poetry
# ----------------------------------------
FROM python:3.11-slim as builder

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala o Poetry
RUN pip install poetry

# Copia os arquivos de configuração do Poetry
COPY pyproject.toml poetry.lock ./

# Instala as dependências de produção, excluindo as de desenvolvimento e o código-fonte
RUN poetry install --without dev --no-root


# ----------------------------------------
# STAGE 2: FINAL - Imagem de Produção Leve
# ----------------------------------------
FROM python:3.11-slim as final

# Define o diretório de trabalho
WORKDIR /app

# Cria o diretório de dados (onde o arquivo DuckDB será persistido)
RUN mkdir -p /app/data

# Copia os arquivos de código-fonte
COPY src ./src
# Copia o arquivo .env se for usado para configurações sensíveis (Boa Prática)
COPY .env ./.env 

# Copia as dependências instaladas no estágio de build
# Isso evita reinstalar tudo no estágio final
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Configura o PYTHONPATH para que os módulos internos sejam encontrados
ENV PYTHONPATH=/app/src

# Comando para executar a aplicação
# -m arxiv_scraper.scraper chama a função main()
CMD ["python", "-m", "arxiv_scraper.scraper"]