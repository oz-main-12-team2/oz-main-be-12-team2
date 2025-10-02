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
│   │   ├── urls/
│   │   │   ├── __init__.py
│   │   │   ├── admin_urls.py     # 관리자 기능 URL
│   │   │   └── user_urls.py      # 사용자 기능 URL 
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── admin_views.py     # 관리자 기능
│   │   │   └── user_views.py      # 사용자 기능 
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── filters.py            # 결제내역 조회 필터
│   │   ├── models.py             # 결제 모델
│   │   ├── serializers.py
│   │   └── test_payments.py      # 결제 테스트
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
## 사용자 요구사항 정의서

요구사항 ID | 대분류 | 요구사항 명 | 요구사항 설명 | 비고
-- | -- | -- | -- | --
U_001 | 회원 관리 | 회원가입 | 이메일/비밀번호/이름/주소 입력 후 회원가입, 이메일 인증 후 계정 활성화 | 이메일 인증 필수
U_002 | 회원 관리 | 이메일 인증 | 인증 링크 클릭으로 계정 활성화 | 인증 전까지 로그인 불가
U_003 | 회원 관리 | 로그인 | 이메일/비밀번호로 로그인 | JWT 토큰은 쿠키로 관리
U_004 | 회원 관리 | 소셜 로그인 | 네이버/구글 OAuth로 로그인 | 소셜 사용자는 비밀번호 없음
U_005 | 회원 관리 | 로그아웃 | 쿠키 삭제 및 리프레시 토큰 블랙리스트 처리 | -
U_006 | 회원 관리 | 토큰 갱신 | 리프레시 토큰으로 액세스 토큰 재발급 | -
U_007 | 회원 관리 | 프로필 조회 | 이메일/이름/주소/관리자여부/생성일/수정일 확인 | 본인 정보만 조회
U_008 | 회원 관리 | 프로필 수정 | 이름/주소 수정 | 이메일은 수정 불가
U_009 | 회원 관리 | 비밀번호 변경 | 로그인 상태에서 기존 비밀번호 입력 후 새 비밀번호로 변경 | 소셜 로그인 사용자 불가
U_010 | 회원 관리 | 비밀번호 재설정 요청 | 이메일로 재설정 링크 발송 | 소셜 로그인 사용자 불가
U_011 | 회원 관리 | 비밀번호 재설정 | 링크 통해 새 비밀번호 설정 | 토큰 검증 필요
U_012 | 회원 관리 | 회원 탈퇴 | 계정 삭제 | 관련 데이터 함께 삭제
C_001 | 장바구니 | 장바구니 조회 | 담긴 상품 목록 및 상세정보 확인 | 사용자당 장바구니 1개
C_002 | 장바구니 | 상품 추가 | 상품ID와 수량으로 추가, 중복시 수량 합산 | 수량 최소값 1
C_003 | 장바구니 | 수량 변경 | 특정 상품의 수량 수정 | 수량 최소값 1
C_004 | 장바구니 | 상품 삭제 | 장바구니에서 상품 제거 | -
C_005 | 장바구니 | 전체 비우기 | 장바구니 내 모든 상품 삭제 | 이미 비어있으면 에러
P_001 | 상품 | 상품 목록 조회 | 필터링(상품명/설명/저자/카테고리/가격범위/전체검색), 정렬, 페이지네이션 | 비인증 사용자도 가능
P_002 | 상품 | 상품 상세 조회 | 특정 상품 상세정보 확인 | 비인증 사용자도 가능
P_003 | 상품 | 상품 등록 | 이미지 업로드 포함 상품 등록 | 관리자만 가능
P_004 | 상품 | 상품 수정 | 이미지 변경 가능 상품 수정 | 관리자만 가능, 이미지 자동 관리
P_005 | 상품 | 상품 삭제 | 상품 삭제 | 관리자만 가능, 이미지도 함께 삭제
O_001 | 주문 | 주문 생성 | 장바구니에서 선택한 상품으로 주문 생성, 수령자 정보 입력 | 선택 상품은 장바구니에서 자동 삭제
O_002 | 주문 | 본인 주문 목록 조회 | 본인 주문 목록 최신순 조회 | -
O_003 | 주문 | 본인 주문 상세 조회 | 주문번호, 상품목록, 총금액, 수령자정보, 배송상태 확인 | -
O_004 | 주문 | 주문 수정 | 수령자 정보, 배송상태 변경 | -
O_005 | 주문 | 주문 삭제 | 주문 삭제 | -
PA_001 | 결제 | 결제 생성 | 주문ID와 결제수단으로 결제 생성 | 본인 주문만 가능, 이미 성공한 주문은 재결제 불가
PA_002 | 결제 | 본인 결제내역 조회 | 상태/기간 필터링 가능 | -
PA_003 | 결제 | 본인 결제 상세조회 | 특정 결제 상세정보 확인 | -
PA_004 | 결제 | 결제 취소 | 결제 취소 처리 | -
S_001 | 통계 | 상품 판매 랭킹 조회 | 일간 판매량 기준 Top 10 (순위/상품ID/상품명/판매수량/매출) | 비인증 사용자도 가능
S_002 | 통계 | 대시보드 통계 조회 | 총 사용자수, 총 매출, 총 재고, 오늘 주문수, 일/주/월 판매통계, 최근 30일 추세 | 관리자만 가능
A_001 | 관리자 | 전체 사용자 목록 조회 | 페이지네이션, 최신순 정렬 | 관리자만 가능
A_002 | 관리자 | 사용자 상세 조회 | 특정 사용자 상세정보 확인 | 관리자만 가능
A_003 | 관리자 | 사용자 정보 수정 | 활성화 상태 변경 | 관리자만 가능
A_004 | 관리자 | 사용자 삭제 | 사용자 계정 삭제 | 관리자만 가능, 본인은 삭제 불가
A_005 | 관리자 | 전체 주문 목록 조회 | 페이지네이션, 최신순 정렬 | 관리자만 가능
A_006 | 관리자 | 주문 상세 조회 | 특정 주문 상세정보 확인 | 관리자만 가능
A_007 | 관리자 | 주문 수정 | 배송상태 변경 | 관리자만 가능
A_008 | 관리자 | 주문 삭제 | 주문 삭제 | 관리자만 가능
A_009 | 관리자 | 전체 결제내역 조회 | 상태/기간 필터링, 페이지네이션, 유저정보 포함 | 관리자만 가능
A_010 | 관리자 | 결제 상세조회 | 특정 결제 상세정보 확인 | 관리자만 가능
A_011 | 관리자 | 결제 취소 | 결제 취소 처리 | 관리자만 가능


<!-- notionvc: 965136e6-86aa-4342-a58b-733d83a5ac5e -->

## ERD
데이터베이스 ERD - 핵심 엔티티 간의 관계를 시각화한 ERD입니다.

![erd_image](https://github.com/user-attachments/assets/1dc0b11c-1486-4ae9-988d-2735294c1fce)


## API 명세서
상세한 API 엔드포인트 및 요청/응답 명세는 [Notion 문서](https://www.notion.so/API-268caf5650aa817eafd1e14aeca6ef83)를 참고해주세요.


## 성능 테스트
Locust를 사용한 부하 테스트 결과, 100명 동시 접속 시 평균 응답시간 11ms, RPS 50, 실패율 0%로 안정적인 성능을 확인했습니다. (Docker 환경)

![locust_image](https://github.com/user-attachments/assets/0f06561e-7467-446d-8272-c2ee2e87c501)


### commit 전 테스트 스크립트 수행
```bash
./scripts/test.sh
```
