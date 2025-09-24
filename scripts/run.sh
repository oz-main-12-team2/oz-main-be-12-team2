#!/bin/bash
set -e

echo "==> 마이그레이션 파일 생성..."
python manage.py makemigrations --noinput

echo "==> 마이그레이션 적용..."
python manage.py migrate --noinput

echo "==> 정적 파일 수집..."
python manage.py collectstatic --noinput

echo "==> Site 객체 확인/생성..."
python manage.py shell -c "
from django.contrib.sites.models import Site
Site.objects.get_or_create(
    id=1,
    defaults={'domain': 'localhost:8000', 'name': 'localhost'}
)
print('Site 객체 생성 완료')
"

echo "==> Gunicorn 서버 시작..."
exec gunicorn --bind 0.0.0.0:8000 config.wsgi:application --workers 2