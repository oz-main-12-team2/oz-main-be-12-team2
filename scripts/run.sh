#!/bin/sh

# 명령어가 실패하면 즉시 종료합니다.
set -e

# 새로운 마이그레이션 파일을 생성합니다.
echo "마이그레이션 파일을 생성 중..."
python manage.py makemigrations

# 데이터베이스에 마이그레이션을 적용합니다.
echo "마이그레이션을 적용 중..."
python manage.py migrate

# Gunicorn 서버를 시작합니다.
echo "서버를 시작합니다..."
gunicorn --bind 0.0.0.0:8000 config.wsgi:application --workers 2