#!/bin/bash
# =============================================================================
# verify-instance.sh — EC2 내부에서 요구사항 자체 점검 (SSH 접속 후 실행)
#   bash verify-instance.sh
#
# 점검 항목
#   [4-1] 인터넷 아웃바운드   : curl https://example.com
#   [4-2] Nginx 실행 상태     : systemctl is-active nginx
#   [4-2] localhost 200 응답  : curl http://localhost
#   [4-5] /health 고정 응답   : curl http://localhost/health → OK
# 결과는 스크린샷으로 남겨 README / troubleshooting 증빙에 사용하세요.
# =============================================================================
set -u

PASS=0; FAIL=0
check() {  # check "설명" 명령...
  local desc=$1; shift
  if "$@" >/dev/null 2>&1; then
    printf '  [PASS] %s\n' "$desc"; PASS=$((PASS+1))
  else
    printf '  [FAIL] %s\n' "$desc"; FAIL=$((FAIL+1))
  fi
}
http_code() { curl -s -o /dev/null -m 10 -w '%{http_code}' "$1"; }

echo "=== Task7 인스턴스 점검 ($(hostname), $(date -Is)) ==="

echo "-- 네트워크 (아웃바운드)"
check "curl https://example.com → 200" test "$(http_code https://example.com)" = "200"

echo "-- 웹 서버"
check "nginx 서비스 active"            systemctl is-active --quiet nginx
check "80 포트 LISTEN"                 bash -c "ss -ltn | grep -q ':80 '"
check "curl http://localhost → 200"    test "$(http_code http://localhost)" = "200"
check "curl http://localhost/health → 200" test "$(http_code http://localhost/health)" = "200"
check "/health 본문 == OK"             test "$(curl -s -m 10 http://localhost/health)" = "OK"

echo
echo "-- 상세 출력 (증빙용)"
echo "\$ curl -I https://example.com";    curl -sI -m 10 https://example.com | head -n 1
echo "\$ curl -i http://localhost/health"; curl -si -m 10 http://localhost/health | sed -n '1p;$p'
echo "\$ systemctl is-active nginx";       systemctl is-active nginx

echo
echo "결과: PASS=${PASS}  FAIL=${FAIL}"
[ "$FAIL" -eq 0 ]
