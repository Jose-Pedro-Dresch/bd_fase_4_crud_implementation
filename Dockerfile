FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependência Python
RUN pip install --no-cache-dir psycopg2-binary

# Copia os arquivos do projeto
COPY app.py .
COPY sql/ ./sql/

# Variáveis de ambiente padrão (sobrescritas pelo docker-compose)
ENV DB_HOST=db \
    DB_PORT=5432 \
    DB_NAME=linkedin \
    DB_USER=postgres \
    DB_PASSWORD=123

# Script de entrada
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
