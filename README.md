```markdown
project_name/
├── .github/                # 깃허브 설정 파일
│   └── workflows/          # 하위에 CI / CD 스크립트를 정의
│       ├── checks.yml/     # develop 또는 main 브랜치에 Push 또는 PR Merge 시 데이터 베이스 연결 확인, 코드 포매팅 체크, 테스트 통과 여부를 검사하는 스크립트
│       └── deploy.yml/     # develop 또는 main 브랜치에 Push 또는 Merge시 배포 자동화를 구현한 스크립트 (배포 직전 구현 예정)
├── config/                 # 프로젝트 설정 파일 (settings, urls 등)
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                   # 앱 디렉토리 (앱별로 디렉토리를 나눔)
│   ├── carts/          # 장바구니 앱
│   │   ├── migrations/     # 마이그레이션 파일
│   │   ├── __init__.py
│   │   ├── apps.py         # 앱 설정
│   │   ├── models.py       # 모델 정의
│   │   ├── serializers.py  # 시리얼라이저 정의
│   │   ├── tests.py        # 테스트 코드
│   │   ├── urls.py         # 앱 전용 URL 라우팅
│   │   └── views.py        # 뷰 로직
│   ├── orders/          # 주문내역 앱
│   │   ├── migrations/     # 마이그레이션 파일
│   │   ├── __init__.py
│   │   ├── admin_urls.py   # 관리자 기능 라우터
│   │   ├── admin_views.py  # 관리자 기능 뷰
│   │   ├── apps.py         # 앱 설정
│   │   ├── serializers.py  # 시리얼라이저 정의
│   │   ├── tests.py        # 테스트 코드
│   │   ├── urls.py         # 앱 전용 URL 라우팅
│   │   └── views.py        # 뷰 로직
│   ├── payments/          # 결제내역 앱
│   │   ├── migrations/     # 마이그레이션 파일
│   │   ├── __init__.py
│   │   ├── admin_urls.py   # 관리자 기능 라우터
│   │   ├── admin_views.py  # 관리자 기능 뷰
│   │   ├── apps.py         # 앱 설정
│   │   ├── serializers.py  # 시리얼라이저 정의
│   │   ├── models.py       # 모델 정의
│   │   ├── tests.py        # 테스트 코드
│   │   ├── urls.py         # 앱 전용 URL 라우팅
│   │   └── views.py        # 뷰 로직
│   ├── products/          # 상품 앱
│   │   ├── migrations/     # 마이그레이션 파일
│   │   ├── __init__.py
│   │   ├── admin_urls.py   # 관리자 기능 라우터
│   │   ├── admin_views.py  # 관리자 기능 뷰
│   │   ├── admin_stats.py  # 관리자 기능 - 판매량 기준 집계
│   │   ├── apps.py         # 앱 설정
│   │   ├── serializers.py  # 시리얼라이저 정의
│   │   ├── models.py       # 모델 정의
│   │   ├── tests.py        # 테스트 코드
│   │   ├── urls.py         # 앱 전용 URL 라우팅
│   │   └── views.py        # 뷰 로직
│   ├── users/          # 사용자 앱
    │   ├── migrations/     # 마이그레이션 파일
│   │   ├── __init__.py
│   │   ├── admin_urls.py   # 관리자 기능 라우터
│   │   ├── admin_views.py  # 관리자 기능 뷰
│   │   ├── apps.py         # 앱 설정
│   │   ├── serializers.py  # 시리얼라이저 정의
│   │   ├── models.py       # 모델 정의
│   │   ├── tests.py        # 테스트 코드
│   │   ├── urls.py         # 앱 전용 URL 라우팅
│   │   └── views.py        # 뷰 로직
│   └── utils/          # 공통 사용 부분
│       └── models.py        # 상속 가능한 공통 모델
├── .env                   # 환경변수
├── .env.example           # 환경변수 예시
├── resources/              # 초기 설정 파일 및 스크립트, nginx, docker, kubernetes 의 yaml 파일
│   ├── nginx/
│   │   └── nginx.conf      # 모델 정의
│   ├── docker/
│   │   ├── dockerfile      # 도커 이미지 빌드 파일
│   │   └── docker-compose.yml   # 도커 컨테이너 정의 파일
│   ├── kubernetes/
│   └── scripts/
│       ├── run.sh          # 도커 이미지 빌드 시 최종적으로 실행될 스크립트 ( 일반적으로 서버 실행 명령 )
│       └── test.sh         # 코드 포매팅 및 테스트코드 실행 시 사용되는 스크립트
├── manage.py               # 관리 명령어
├── uv.lock                 # uv 의존성 패키지 설치 정보
└── pyproject.toml          # poetry 의존성 패키지 목록 및 설정
```

### commit 전 테스트 스크립트 수행
```bash
./scripts/test.sh
```