#!/bin/bash
set -e

# 마이그레이션 체크 및 적용
python manage.py makemigrations --check --noinput
python manage.py migrate

# Gunicorn 실행
gunicorn --bind 0.0.0.0:8000 config.wsgi:application --workers 2
