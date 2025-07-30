#!/bin/sh
mkdir -p logs
touch logs/certificate.log
chmod 664 logs/certificate.log
uv run manage.py migrate --noinput
uv run python manage.py runserver ${HOST}:${PORT}
