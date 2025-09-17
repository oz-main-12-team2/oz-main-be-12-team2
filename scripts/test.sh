set -eo pipefail  # 실패하면 더 진행하지 않음 -> 왜 실패했는지 조사 가능

COLOR_GREEN=`tput setaf 2;`  # 초록색 출력
COLOR_NC=`tput sgr0;`        # 색상 초기화

# -----------------------------------------------------------
# ruff: unused import + import 정렬(I 규칙) 자동 수정
# -----------------------------------------------------------
echo "Starting ruff (auto-fix: imports only)"
uv run ruff check --select F401,I --fix .
echo "OK"

# -----------------------------------------------------------
# ruff: 포맷터 실행 (개행, 따옴표, 정렬 등 자동 수정)
# -----------------------------------------------------------
echo "Starting ruff format"
uv run ruff format .
echo "OK"

# -----------------------------------------------------------
# ruff: 의미 있는 코드 오류(F/E/W) → 리포트만, 자동 수정 없음
# -----------------------------------------------------------
echo "Starting ruff (report only: other issues)"
uv run ruff check --extend-select F,E,W --no-fix .
echo "OK"

# -----------------------------------------------------------
# mypy: 타입 체크 (코드 오류 잡기)
# -----------------------------------------------------------
#echo "Starting mypy"
#uv run dmypy run -- .
#echo "OK"

# -----------------------------------------------------------
# pytest + coverage: 단위 테스트 실행 및 커버리지 리포트 생성
# -----------------------------------------------------------
echo "Starting pytest with coverage"
uv run coverage run manage.py test
uv run coverage report -m
uv run coverage html

echo "${COLOR_GREEN}All tests passed successfully!${COLOR_NC}"