#!/bin/sh
mkdir -p logs
touch src/logs/certificates.log
chmod 664 src/logs/certificates.log
uv run manage.py migrate --noinput
uv run python manage.py runserver ${HOST}:${PORT}
