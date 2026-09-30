#!/bin/bash
# =============================================================================
# verify-external.sh — 내 PC(macOS/Linux/Git Bash)에서 외부 접속 검증  [요구사항 4-5 (B)]
#   bash scripts/verify-external.sh <퍼블릭IP>
# =============================================================================
set -u
IP=${1:?"사용법: $0 <퍼블릭IP>"}

echo "=== Task7 외부 접속 검증 ($(date '+%Y-%m-%dT%H:%M:%S')) ==="
echo "\$ curl -i http://${IP}/health"
curl -si -m 10 "http://${IP}/health" || { echo "[FAIL] /health 응답 없음"; exit 1; }
echo
code_root=$(curl -s -o /dev/null -m 10 -w '%{http_code}' "http://${IP}/")
code_health=$(curl -s -o /dev/null -m 10 -w '%{http_code}' "http://${IP}/health")
body_health=$(curl -s -m 10 "http://${IP}/health")

echo "GET /        → ${code_root}"
echo "GET /health  → ${code_health}  body=${body_health}"

if [ "$code_health" = "200" ] && [ "$body_health" = "OK" ]; then
  echo "[PASS] 외부 접속 검증 성공"
else
  echo "[FAIL] 기대값: 200 / OK"; exit 1
fi
