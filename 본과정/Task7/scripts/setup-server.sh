#!/bin/bash
# =============================================================================
# setup-server.sh — EC2(Ubuntu)에 Nginx 설치 + 웹 페이지 + /health 엔드포인트 배포
#
# 사용법
#   1) EC2 생성 시 "사용자 데이터(User data)"에 파일 내용을 그대로 붙여넣기  (자동 실행, root 권한)
#   2) 또는 SSH 접속 후 수동 실행:  sudo bash setup-server.sh
#
# 결과
#   GET /        → 200, "Hello Cloud" 페이지
#   GET /health  → 200, "OK"
#   로그         → /var/log/setup-server.log
# =============================================================================
set -euo pipefail
exec > >(tee -a /var/log/setup-server.log) 2>&1

echo "[setup] start: $(date -Is)"

if [ "$(id -u)" -ne 0 ]; then
  echo "[setup] ERROR: root 권한 필요 (sudo bash setup-server.sh)" >&2
  exit 1
fi

# --- 1. 패키지 설치 -----------------------------------------------------------
if command -v apt-get >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -y
  apt-get install -y nginx curl
  WEB_ROOT=/var/www/html
  SITE_CONF=/etc/nginx/sites-available/default
elif command -v dnf >/dev/null 2>&1; then          # Amazon Linux 2023
  dnf install -y nginx
  WEB_ROOT=/usr/share/nginx/html
  SITE_CONF=/etc/nginx/conf.d/task7.conf
else
  echo "[setup] ERROR: 지원하지 않는 OS (Ubuntu / Amazon Linux 2023만 지원)" >&2
  exit 1
fi

# --- 2. 인스턴스 메타데이터(IMDSv2)로 표시용 정보 조회 -------------------------
imds() {
  local token
  token=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
          -H "X-aws-ec2-metadata-token-ttl-seconds: 60" || true)
  curl -s -H "X-aws-ec2-metadata-token: ${token}" \
       "http://169.254.169.254/latest/meta-data/$1" || echo "unknown"
}
INSTANCE_ID=$(imds instance-id)
AZ=$(imds placement/availability-zone)
PRIVATE_IP=$(imds local-ipv4)

# --- 3. 웹 페이지 ---------------------------------------------------------------
mkdir -p "${WEB_ROOT}"
cat > "${WEB_ROOT}/index.html" <<HTML
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hello Cloud — Task7</title>
  <style>
    body { margin:0; min-height:100vh; display:flex; align-items:center; justify-content:center;
           font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background:#0f172a; color:#e2e8f0; }
    .card { background:#1e293b; padding:40px 48px; border-radius:16px; max-width:520px;
            box-shadow:0 10px 30px rgba(0,0,0,.4); }
    h1 { margin:0 0 8px; font-size:2.2rem; color:#38bdf8; }
    p  { margin:4px 0; color:#94a3b8; }
    table { margin-top:20px; border-collapse:collapse; width:100%; font-size:.95rem; }
    td { padding:6px 0; border-bottom:1px solid #334155; }
    td:first-child { color:#64748b; width:45%; }
    code { color:#fbbf24; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Hello Cloud</h1>
    <p>VPC · Public Subnet · IGW · Security Group · EC2(Nginx)</p>
    <table>
      <tr><td>Instance ID</td><td>${INSTANCE_ID}</td></tr>
      <tr><td>Availability Zone</td><td>${AZ}</td></tr>
      <tr><td>Private IP</td><td>${PRIVATE_IP}</td></tr>
      <tr><td>Health Check</td><td><code>GET /health → OK</code></td></tr>
    </table>
  </div>
</body>
</html>
HTML

# --- 4. Nginx 설정: / + /health -------------------------------------------------
cat > "${SITE_CONF}" <<NGINX
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    root ${WEB_ROOT};
    index index.html;

    # 헬스체크: 항상 200 + 고정 문구 "OK"
    location = /health {
        access_log off;
        default_type text/plain;
        return 200 "OK\n";
    }

    location / {
        try_files \$uri \$uri/ =404;
    }
}
NGINX

# Amazon Linux 기본 server 블록과 default_server 충돌 방지
if [ -f /etc/nginx/nginx.conf ] && [ "${SITE_CONF}" = "/etc/nginx/conf.d/task7.conf" ]; then
  sed -i 's/listen\s\+80 default_server;/listen 80;/; s/listen\s\+\[::\]:80 default_server;/listen [::]:80;/' /etc/nginx/nginx.conf
fi

nginx -t
systemctl enable nginx
systemctl restart nginx

# --- 5. 자체 검증 --------------------------------------------------------------
sleep 1
echo "[setup] localhost /       → HTTP $(curl -s -o /dev/null -w '%{http_code}' http://localhost/)"
echo "[setup] localhost /health → HTTP $(curl -s -o /dev/null -w '%{http_code}' http://localhost/health) body=$(curl -s http://localhost/health)"
echo "[setup] done: $(date -Is)"
