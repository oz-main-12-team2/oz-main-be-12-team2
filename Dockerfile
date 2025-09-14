# 1단계: 빌드 스테이지 (uv 바이너리 복사)
FROM python:3.13-slim AS builder

# uv 공식 이미지에서 바이너리 복사
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# 의존성 파일 복사
COPY pyproject.toml uv.lock ./

# 의존성 설치 (uv 실행 가능)
RUN uv sync --all-packages --no-install-project

# 전체 프로젝트 복사
COPY . .

# 프로젝트 및 의존성 완성
RUN uv sync --all-packages

# 2단계: 실제 실행 이미지
FROM python:3.13-slim

# bash 및 PostgreSQL client 설치 (pg_isready 포함)
RUN apt-get update && apt-get install -y bash postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 빌드 스테이지에서 완성된 /app 폴더 복사
COPY --from=builder /app /app
COPY --from=builder /bin/uv /bin/uv
COPY ./scripts /scripts

# 도커 & 장고 호환관련
RUN /app/.venv/bin/python manage.py collectstatic --noinput

# 실행 스크립트 권한 설정 및 dos2unix 처리 (Windows CRLF 방지)
RUN chmod +x /scripts/run.sh && apt-get update && apt-get install -y dos2unix \
    && dos2unix /scripts/run.sh \
    && rm -rf /var/lib/apt/lists/*

# uv 환경 PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# 실행 스크립트
CMD ["/bin/bash", "/scripts/run.sh"]
