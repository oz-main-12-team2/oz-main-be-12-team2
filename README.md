```markdown
project_name/
├── .github/                # 깃허브 설정 파일 ( 커밋템플릿, 이슈템플릿, pr 템플릿, CI / CD 등 )
│   ├── COMMIT_TEMPLATE/    # 하위에 커밋 템플릿을 정의
│   ├── ISSUE_TEMPLATE/     # 하위에 이슈템플릿을 정의
│   └── workflows/          # 하위에 CI / CD 스크립트를 정의
│       ├── checks.yml/     # develop 또는 main 브랜치에 Push 또는 PR Merge 시 데이터 베이스 연결 확인, 코드 포매팅 체크, 테스트 통과 여부를 검사하는 스크립트
│       └── deploy.yml/     # develop 또는 main 브랜치에 Push 또는 Merge시 배포 자동화를 구현한 스크립트
├── config/                 # 프로젝트 설정 파일 (settings, urls 등)
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                   # 앱 디렉토리 (앱별로 디렉토리를 나눔)
│   ├── app_name1/
│   │   ├── migrations/     # 마이그레이션 파일
│   │   ├── services/       # 앱에서 사용되는 서비스 로직을 구현하는 폴더
│   │   ├── repository/     # 앱의 데이터베이스 모델에 관련된 CRUD 동작을 정의하는 폴더
│   │   ├── admin.py        # Django Admin 관련 설정
│   │   ├── apps.py         # 앱 설정
│   │   ├── models.py       # 모델 정의
│   │   ├── tests.py        # 테스트 코드
│   │   ├── urls.py         # 앱 전용 URL 라우팅
│   │   └── views.py        # 뷰 로직
│   ├── app_name2/          # 다른 앱
│   │   ├── migrations/     # 마이그레이션 파일
│   │   ├── services/       # 앱에서 사용되는 서비스 로직을 구현하는 폴더
│   │   ├── repository/     # 앱의 데이터베이스 모델에 관련된 CRUD 동작을 정의하는 폴더
│   │   ├── admin.py        # Django Admin 관련 설정
│   │   ├── apps.py         # 앱 설정
│   │   ├── models.py       # 모델 정의
│   │   ├── tests.py        # 테스트 코드
│   │   ├── urls.py         # 앱 전용 URL 라우팅
│   │   └── views.py        # 뷰 로직
│   └── ...
├── envs/                   # 환경변수 파일들
│   ├── .env.local          # 로컬 환경에서 서버 구동 및 테스트 시 필요한 환경변수
│   └── .env.prod           # 배포 환경에서 서버 구동 및 테스트 시 필요한 환경변수
├── resources/              # 초기 설정 파일 및 스크립트, nginx, docker, kubernetes 의 yaml 파일
│   ├── nginx/
│   │   └── nginx.conf      # 모델 정의
│   ├── docker/
│   │   ├── dockerfile      # 도커 이미지 빌드 파일
│   │   └── docker-compose.yml   # 도커 컨테이너 정의 파일
│   ├── kubernetes/
│   └── scripts/
│       ├── entrypoint.sh   # 도커 이미지 빌드 시 최종적으로 실행될 스크립트 ( 일반적으로 서버 실행 명령 )
│       └── test.sh         # 코드 포매팅 및 테스트코드 실행 시 사용되는 스크립트
├── manage.py               # 관리 명령어
├── poetry.lock             # poetry 의존성 패키지 설치 정보
└── pyproject.toml          # poetry 의존성 패키지 목록 및 설정
```