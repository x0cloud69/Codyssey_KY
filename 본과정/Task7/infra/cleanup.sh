#!/bin/bash
# =============================================================================
# cleanup.sh — provision.sh 로 만든 리소스를 "의존성 역순"으로 삭제 + 잔존 여부 검증
#
#   삭제 순서 (앞 리소스가 뒤 리소스를 참조하므로 역순으로 지워야 함)
#   EC2 종료(→ EBS 자동 삭제) → Elastic IP 해제 → Key Pair → Security Group
#   → Route Table 연결 해제/삭제 → IGW Detach/삭제 → Subnet → VPC
#
# 사용법:  bash infra/cleanup.sh
# 결과는 docs/cleanup-checklist.md 에 근거(출력 캡처)로 남기세요.
# =============================================================================
set -uo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
STATE_FILE="$SCRIPT_DIR/state.env"
export AWS_PROFILE=${AWS_PROFILE:-task7}
export AWS_REGION=ap-northeast-2
export AWS_DEFAULT_REGION=ap-northeast-2
export AWS_PAGER=""

[ -f "$STATE_FILE" ] || { echo "$STATE_FILE 없음 — 콘솔에서 수동 정리하세요 (docs/cleanup-checklist.md)" >&2; exit 1; }
# shellcheck disable=SC1090
source "$STATE_FILE"

# aws.exe 출력을 파이프(|)로 바로 받으면, aws.exe 가 띄운 백그라운드 프로세스가 파이프를 붙잡아
# 명령이 끝났는데도 스크립트가 멈출 수 있다 → 임시 파일로 받은 뒤 CR 제거. 입력 대기도 차단(</dev/null).
aws() {
  local out rc
  out=$(mktemp)
  command aws --cli-connect-timeout 15 --cli-read-timeout 60 "$@" </dev/null >"$out"
  rc=$?
  tr -d '\r' <"$out"
  rm -f "$out"
  return $rc
}
log() { printf '\033[33m[cleanup]\033[0m %s\n' "$*"; }
run() { "$@" >/dev/null 2>&1 && log "OK   $*" || log "SKIP $* (이미 없음 또는 실패)"; }

# 1. EC2 ------------------------------------------------------------------------
if [ -n "${INSTANCE_ID:-}" ]; then
  VOL_IDS=$(aws ec2 describe-volumes --filters "Name=attachment.instance-id,Values=$INSTANCE_ID" \
            --query 'Volumes[].VolumeId' --output text 2>/dev/null || true)
  run aws ec2 terminate-instances --instance-ids "$INSTANCE_ID"
  log "EC2 종료 대기..."
  aws ec2 wait instance-terminated --instance-ids "$INSTANCE_ID"
  # DeleteOnTermination=false 였거나 수동으로 붙인 볼륨 대비
  for v in $VOL_IDS; do
    aws ec2 wait volume-deleted --volume-ids "$v" 2>/dev/null || run aws ec2 delete-volume --volume-id "$v"
  done
fi

# 2. Elastic IP (프로젝트 태그 또는 수동 할당분) ----------------------------------
for alloc in $(aws ec2 describe-addresses --filters "Name=tag:Project,Values=task7" \
               --query 'Addresses[].AllocationId' --output text); do
  run aws ec2 release-address --allocation-id "$alloc"
done
[ -n "${EIP_ALLOC_ID:-}" ] && run aws ec2 release-address --allocation-id "$EIP_ALLOC_ID"

# 3. Key Pair (로컬 .pem 파일은 직접 삭제/보관 결정) ------------------------------
[ -n "${KEY_NAME:-}" ] && run aws ec2 delete-key-pair --key-name "$KEY_NAME"

# 4. Security Group --------------------------------------------------------------
[ -n "${SG_ID:-}" ] && run aws ec2 delete-security-group --group-id "$SG_ID"

# 5. Route Table -----------------------------------------------------------------
[ -n "${RTB_ASSOC_ID:-}" ] && run aws ec2 disassociate-route-table --association-id "$RTB_ASSOC_ID"
[ -n "${RTB_ID:-}" ]       && run aws ec2 delete-route-table --route-table-id "$RTB_ID"

# 6. Internet Gateway ------------------------------------------------------------
if [ -n "${IGW_ID:-}" ]; then
  run aws ec2 detach-internet-gateway --internet-gateway-id "$IGW_ID" --vpc-id "$VPC_ID"
  run aws ec2 delete-internet-gateway --internet-gateway-id "$IGW_ID"
fi

# 7. Subnet → VPC ----------------------------------------------------------------
[ -n "${SUBNET_ID:-}" ] && run aws ec2 delete-subnet --subnet-id "$SUBNET_ID"
[ -n "${VPC_ID:-}" ]    && run aws ec2 delete-vpc --vpc-id "$VPC_ID"

# 8. 잔존 리소스 검증 (체크리스트 근거) -----------------------------------------
echo
echo "================ 정리 결과 검증 ($(date '+%Y-%m-%dT%H:%M:%S')) ================"
count() { local n; n=$(echo "$1" | wc -w); printf '  %-28s %s\n' "$2" "$( [ "$n" -eq 0 ] && echo "0 ✅" || echo "$n ❌  $1")"; }

count "$(aws ec2 describe-instances --filters "Name=tag:Project,Values=task7" \
        "Name=instance-state-name,Values=pending,running,stopping,stopped" \
        --query 'Reservations[].Instances[].InstanceId' --output text)"          "EC2 (terminated 제외)"
count "$(aws ec2 describe-volumes --query 'Volumes[].VolumeId' --output text)"   "EBS 볼륨 (리전 전체)"
count "$(aws ec2 describe-addresses --query 'Addresses[].PublicIp' --output text)" "Elastic IP (리전 전체)"
count "$(aws ec2 describe-internet-gateways --filters "Name=tag:Project,Values=task7" \
        --query 'InternetGateways[].InternetGatewayId' --output text)"         "Internet Gateway (task7)"
count "$(aws ec2 describe-vpcs --filters "Name=tag:Project,Values=task7" \
        --query 'Vpcs[].VpcId' --output text)"                                 "VPC (task7)"
count "$(aws ec2 describe-nat-gateways --filter "Name=state,Values=pending,available" \
        --query 'NatGateways[].NatGatewayId' --output text)"                   "NAT Gateway (리전 전체)"
echo "==========================================================================="

mv "$STATE_FILE" "$STATE_FILE.deleted-$(date +%Y%m%d%H%M%S)"
log "state.env → 보관 처리 완료. Billing Dashboard 도 확인하세요."
