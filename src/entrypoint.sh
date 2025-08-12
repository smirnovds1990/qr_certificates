#!/bin/sh
mkdir -p logs
touch src/logs/certificate.log
chmod 664 src/logs/certificate.log
uv run manage.py migrate --noinput
uv run python manage.py runserver ${HOST}:${PORT}
