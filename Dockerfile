# 1단계: 빌드 스테이지
FROM python:3.13-slim AS builder

# uv 복사
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# 의존성 파일 복사
COPY pyproject.toml uv.lock ./

# 의존성 설치 (프로젝트 제외)
RUN uv sync --all-packages --no-install-project

# 전체 프로젝트 복사
COPY . .

# 프로젝트 및 의존성 설치 완료
RUN uv sync --all-packages


# 2단계: 실행 이미지
FROM python:3.13-slim

# bash, PostgreSQL client, dos2unix 설치
RUN apt-get update && apt-get install -y bash postgresql-client dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 빌드 스테이지에서 복사
COPY --from=builder /app /app
COPY --from=builder /bin/uv /bin/uv
COPY resources/scripts /scripts

# 실행 스크립트 권한 및 CRLF 변환
RUN chmod +x /scripts/run.sh && dos2unix /scripts/run.sh

# 가상환경 PATH 추가
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# run.sh 실행
CMD ["/bin/bash", "/scripts/run.sh"]