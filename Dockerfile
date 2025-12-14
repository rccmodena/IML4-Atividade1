# Estágio 1: Build (para instalar as dependências)
# Usamos uma imagem base leve e específica para a versão do Python.
FROM python:3.11-slim as builder

# Define o diretório de trabalho dentro da imagem
WORKDIR /app

# Copia os arquivos de configuração do Poetry para o ambiente de build
COPY pyproject.toml poetry.lock ./

# Instala o Poetry
RUN pip install poetry

# Configura o Poetry para não criar ambientes virtuais dentro do container
RUN poetry config virtualenvs.create false

# Instala as dependências de produção
RUN poetry install --only main

# Estágio 2: Produção (Runtime)
# Imagem ainda mais leve para o ambiente de execução
FROM python:3.11-slim as runtime

WORKDIR /app

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1

# Copia as dependências instaladas do estágio 'builder'
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copia o código-fonte (src) e o arquivo de configuração (.env)
COPY ./src /app/src
COPY ./.env /app/.env

# Comando de entrada para rodar a aplicação
CMD ["python", "-m", "arxiv_scraper.scraper"]