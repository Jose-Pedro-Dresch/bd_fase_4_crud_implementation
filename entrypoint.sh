#!/bin/bash
set -e

echo ""
echo "  Aguardando o banco de dados ficar pronto..."

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; do
  sleep 1
done

echo "  Banco de dados pronto!"
echo ""

# Injeta as variáveis de ambiente no DB_CONFIG do app.py em tempo de execução
python3 - << 'PYEOF'
import os, re

path = "/app/app.py"
with open(path, "r") as f:
    content = f.read()

new_config = f"""DB_CONFIG = {{
    "dbname":   "{os.environ.get('DB_NAME',     'linkedin')}",
    "user":     "{os.environ.get('DB_USER',     'postgres')}",
    "password": "{os.environ.get('DB_PASSWORD', '123')}",
    "host":     "{os.environ.get('DB_HOST',     'localhost')}",
    "port":     "{os.environ.get('DB_PORT',     '5432')}"
}}"""

content = re.sub(
    r'DB_CONFIG\s*=\s*\{[^}]+\}',
    new_config,
    content,
    count=1
)

with open(path, "w") as f:
    f.write(content)
PYEOF

exec python3 /app/app.py
