#!/bin/bash
set -e

# 새로운 마이그레이션 파일을 생성합니다.
echo "마이그레이션 파일을 생성 중..."
python manage.py makemigrations

# 데이터베이스에 마이그레이션을 적용합니다.
echo "마이그레이션을 적용 중..."
python manage.py migrate

# Site 객체 생성
echo "Site 객체를 생성 중..."
python manage.py shell -c "
from django.contrib.sites.models import Site
Site.objects.get_or_create(id=1, defaults={'domain': 'localhost:8000', 'name': 'localhost'})
print('Site 객체 생성 완료')
"

# Gunicorn 서버를 시작합니다.
echo "서버를 시작합니다..."
gunicorn --bind 0.0.0.0:8000 config.wsgi:application --workers 2