#!/bin/bash

LOG_FILE="/var/log/agent-app/monitor.log"
APP_NAME="agent-app"
APP_PORT="15034"

timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

warning() {
  echo "[$(timestamp)] [WARNING] $1"
}

fail() {
  echo "[$(timestamp)] [ERROR] $1"
  exit 1
}

rotate_log() {
  if [ -f "$LOG_FILE" ] && [ "$(stat -c%s "$LOG_FILE")" -ge 10485760 ]; then
    for i in 9 8 7 6 5 4 3 2 1; do
      [ -f "${LOG_FILE}.${i}" ] && mv "${LOG_FILE}.${i}" "${LOG_FILE}.$((i + 1))"
    doneㅣ
    mv "$LOG_FILE" "${LOG_FILE}.1"
    touch "$LOG_FILE"
  fi
}

# Health Check: process
pgrep -f "$APP_NAME" > /dev/null || fail "Process not running: $APP_NAME"

# Health Check: port
ss -H -ltn | awk '{print $1, $4}' | grep -q "LISTEN 0.0.0.0:${APP_PORT}" \
  || fail "Port not listening on 0.0.0.0:${APP_PORT}"

# Firewall check: warning only
if command -v ufw > /dev/null 2>&1; then
  ufw status | grep -qi "Status: active" || warning "UFW is not active"
elif command -v firewall-cmd > /dev/null 2>&1; then
  firewall-cmd --state 2>/dev/null | grep -q "running" || warning "firewalld is not active"
else
  warning "No firewall tool found: ufw/firewalld"
fi

# Resource collection
CPU=$(awk '
  NR==1 { idle1=$5; total1=0; for (i=2; i<=NF; i++) total1+=$i }
  NR==2 { idle2=$5; total2=0; for (i=2; i<=NF; i++) total2+=$i }
  END { printf "%.1f", (1 - (idle2-idle1)/(total2-total1)) * 100 }
' < <(grep "^cpu " /proc/stat; sleep 1; grep "^cpu " /proc/stat))

MEM=$(free | awk '/Mem:/ { printf "%.1f", ($3 / $2) * 100 }')
DISK_USED=$(df / | awk 'NR==2 { gsub("%", "", $5); print $5 }')
PID=$(pgrep -f "$APP_NAME" | head -n 1)

awk "BEGIN { exit !($CPU > 20) }" && warning "CPU usage is high: ${CPU}%"
awk "BEGIN { exit !($MEM > 10) }" && warning "Memory usage is high: ${MEM}%"
[ "$DISK_USED" -gt 80 ] && warning "Disk usage is high: ${DISK_USED}%"

rotate_log

echo "[$(timestamp)] PID:${PID} CPU:${CPU}% MEM:${MEM}% DISK_USED:${DISK_USED}%" >> "$LOG_FILE"