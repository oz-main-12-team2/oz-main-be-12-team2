```markdown
oz-main-be-12-team2/
├── .github/                      # 깃허브 설정 파일
│   └── workflows/                # 하위에 CI / CD 스크립트를 정의
│       ├── checks.yml/           # develop 또는 main 브랜치에 Push 또는 PR Merge 시 데이터 베이스 연결 확인, 코드 포매팅 체크, 테스트 통과 여부를 검사하는 스크립트
│       └── deploy.yml/           # develop 또는 main 브랜치에 Push 또는 Merge시 배포 자동화를 구현한 스크립트 (배포 직전 구현 예정)
├── apps                          # Django 앱 디렉토리
│   ├── __init__.py
│   ├── carts                     # 장바구니 기능
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py             # 장바구니 모델
│   │   ├── serializers.py        # API 직렬화
│   │   ├── signals.py            # Django 시그널
│   │   ├── test_carts.py         # 장바구니 테스트
│   │   ├── urls.py               # URL 라우팅
│   │   └── views.py              # API 뷰
│   ├── orders                    # 주문 관리
│   │   ├── __init__.py
│   │   ├── admin.py              # Django 관리자
│   │   ├── admin_urls.py         # 관리자 URL
│   │   ├── admin_views.py        # 관리자 뷰
│   │   ├── apps.py
│   │   ├── models.py             # 주문 모델
│   │   ├── serializers.py
│   │   ├── test_orders.py        # 주문 테스트
│   │   ├── urls.py
│   │   └── views.py
│   ├── payments                  # 결제 처리
│   │   ├── __init__.py
│   │   ├── admin_urls.py
│   │   ├── admin_views.py
│   │   ├── apps.py
│   │   ├── models.py             # 결제 모델
│   │   ├── serializers.py
│   │   ├── test_payments.py      # 결제 테스트
│   │   ├── urls.py
│   │   └── views.py
│   ├── products                  # 상품 관리
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── admin_urls.py
│   │   ├── admin_views.py
│   │   ├── apps.py
│   │   ├── filters.py            # 상품 필터링
│   │   ├── models.py             # 상품 모델
│   │   ├── serializers.py
│   │   ├── signals.py
│   │   ├── test_products.py      # 상품 테스트
│   │   ├── urls.py
│   │   └── views.py
│   ├── stats                     # 통계 기능
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── serializers.py
│   │   ├── test_stats.py         # 통계 테스트
│   │   ├── urls.py
│   │   └── views.py
│   ├── support                   # 고객 지원
│   │   ├── __init__.py
│   │   ├── admin_urls.py
│   │   ├── admin_views.py
│   │   ├── apps.py
│   │   ├── gemini_service.py     # Gemini AI 연동
│   │   ├── models.py             # 문의 모델
│   │   ├── serializers.py
│   │   ├── tests                 # 지원 테스트 모음
│   │   ├── urls.py
│   │   └── views.py
│   ├── users                     # 사용자 관리
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── admin_urls.py
│   │   ├── admin_views.py
│   │   ├── apps.py
│   │   ├── middleware.py         # 인증 미들웨어
│   │   ├── models.py             # 사용자 모델
│   │   ├── serializers.py
│   │   ├── social_utils.py       # 소셜 로그인 유틸
│   │   ├── social_views.py       # 소셜 로그인 뷰
│   │   ├── tests                 # 사용자 테스트 모음
│   │   ├── urls.py
│   │   └── views.py
│   └── utils                     # 공통 유틸리티
│       ├── models.py             # 공통 모델
│       └── pagination.py         # 페이지네이션
├── check_email.py                # 이메일 확인 스크립트
├── config                        # Django 설정
│   ├── __init__.py
│   ├── asgi.py                   # ASGI 설정
│   ├── settings.py               # 프로젝트 설정
│   ├── urls.py                   # 메인 URL 설정
│   └── wsgi.py                   # WSGI 설정
├── docker-compose.yml            # Docker Compose 설정
├── locust_tests                  # 부하 테스트
│   └── locustfile.py             # Locust 시나리오
├── Dockerfile                    # Docker 컨테이너 설정
├── README.md                     # 프로젝트 문서
├── main.py                       # 애플리케이션 진입점
├── manage.py                     # Django 관리 명령어
├── pyproject.toml                # 프로젝트 메타데이터
├── requirements.txt              # Python 의존성
└── scripts                       # 실행 스크립트
    ├── run.sh                    # 서버 실행
    └── test.sh                   # 테스트 실행
```

### commit 전 테스트 스크립트 수행
```bash
./scripts/test.sh
```
