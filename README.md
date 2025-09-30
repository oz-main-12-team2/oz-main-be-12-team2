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
│   ├── core                      # 공통 유틸리티 앱
│   │   ├── __init__.py           
│   │   ├── models.py             # 공통 모델
│   │   └── pagination.py         # 공통 페이지네이션
│   ├── orders                    # 주문 관리
│   │   ├── __init__.py
│   │   ├── admin.py              # 관리자 주문 모델
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
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── admin_dashboard_view.py     # 관리자 페이지 대시보드
│   │   │   └── product_ranking_view.py     # 상품 랭킹 
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── serializers.py
│   │   ├── test_stats.py         # 통계 테스트
│   │   └── urls.py
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
│   └── users                     # 사용자 관리
│       ├── __init__.py
│       ├── admin.py
│       ├── admin_urls.py
│       ├── admin_views.py
│       ├── apps.py
│       ├── middleware.py         # 인증 미들웨어
│       ├── models.py             # 사용자 모델
│       ├── serializers.py
│       ├── social_utils.py       # 소셜 로그인 유틸
│       ├── social_views.py       # 소셜 로그인 뷰
│       ├── tests                 # 사용자 테스트 모음
│       ├── urls.py
│       └── views.py
├── config                        # Django 설정
│   ├── __init__.py
│   ├── asgi.py                   # ASGI 설정
│   ├── settings.py               # 프로젝트 설정
│   ├── urls.py                   # 메인 URL 설정
│   └── wsgi.py                   # WSGI 설정
├── locust_tests                  # 부하 테스트
│   └── locustfile.py             # Locust 시나리오
├── resources            
│   ├── nginx.conf                # nginx 설정
│   └── scripts/
│       ├── run.sh                # 서버 실행 스크립트
│       └── test.sh               # 테스트 실행 스크립트
├── .dockerignore                 
├── .env.example                  # 환경변수 예시
├── .gitignore                  
├── docker-compose.yml            # Docker Compose 설정
├── Dockerfile                    # Docker 컨테이너 설정
├── manage.py                     # Django 관리 명령어
├── pyproject.toml                # 프로젝트 메타데이터
├── README.md                     # 프로젝트 문서
└── uv.lock                       # uv 의존성
```

## 성능 테스트
Locust를 사용한 부하 테스트 결과, 100명 동시 접속 시 평균 응답시간 11ms, RPS 50, 실패율 0%로 안정적인 성능을 확인했습니다. (Docker 환경)

![image](https://github.com/user-attachments/assets/0f06561e-7467-446d-8272-c2ee2e87c501)

### commit 전 테스트 스크립트 수행
```bash
./scripts/test.sh
```
