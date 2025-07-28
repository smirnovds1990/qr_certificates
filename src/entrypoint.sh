#!/bin/sh
uv run manage.py makemigrations --noinput
uv run manage.py migrate --noinput
uv run python manage.py runserver
