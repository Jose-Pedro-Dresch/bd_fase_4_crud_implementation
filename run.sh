#!/bin/bash
set -e

IMAGE_NAME="linkedin_app"
DB_CONTAINER="linkedin_db"
NETWORK=$(docker inspect --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' $DB_CONTAINER)

echo ""
echo "  [1/3] Construindo a imagem da aplicação..."
docker build -t $IMAGE_NAME . --quiet

echo "  [2/3] Subindo o banco de dados..."
docker compose up -d db

echo "  [3/3] Aguardando o banco ficar saudável..."
until docker inspect --format='{{.State.Health.Status}}' $DB_CONTAINER 2>/dev/null | grep -q "healthy"; do
  sleep 2
done

echo ""
echo "  Tudo pronto! Iniciando a aplicação..."
echo ""

# Roda o app com -it para garantir terminal interativo real
docker run --rm -it \
  --network $NETWORK \
  -e DB_HOST=$DB_CONTAINER \
  -e DB_PORT=5432 \
  -e DB_NAME=linkedin \
  -e DB_USER=postgres \
  -e DB_PASSWORD=123 \
  $IMAGE_NAME
