#!/bin/sh
set -e

python manage.py makemigrations --check --noinput
python manage.py migrate
gunicorn --bind 0.0.0.0:8000 config.wsgi:application --workers 2