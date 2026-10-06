#!/bin/bash
# =============================================================================
# provision.sh — AWS CLI로 Task7 인프라 전체 생성 (서울 리전)
#
#   VPC(10.0.0.0/16) ─ Public Subnet(10.0.1.0/24) ─ Route Table(0.0.0.0/0 → IGW)
#   Security Group: 80 ← 0.0.0.0/0 / 22 ← 내 IP/32
#   EC2 t3.micro (Ubuntu 24.04, gp3 8GiB) + user-data(setup-server.sh)
#
# 사전 준비
#   - AWS CLI v2 설치, `aws configure --profile task7` 로 IAM 사용자(task7-user) 자격증명 등록
#   - Windows: Git Bash 또는 WSL 에서 실행
#
# 사용법
#   bash infra/provision.sh                      # 내 IP 자동 조회
#   MY_IP=1.2.3.4 bash infra/provision.sh        # 내 IP 직접 지정
#   INSTANCE_TYPE=t2.micro bash infra/provision.sh
#
# 생성된 리소스 ID는 infra/state.env 에 저장 → cleanup.sh 가 사용
# =============================================================================
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
STATE_FILE="$SCRIPT_DIR/state.env"

export AWS_PROFILE=${AWS_PROFILE:-task7}
export AWS_REGION=ap-northeast-2
export AWS_DEFAULT_REGION=ap-northeast-2
export AWS_PAGER=""
# Git Bash(MSYS)가 "/aws/service/..." , "DeviceName=/dev/sda1" 같은 인자를 Windows 경로로 바꾸지 않도록 변환 끄기
export MSYS_NO_PATHCONV=1
export MSYS2_ARG_CONV_EXCL="*"

cd "$ROOT_DIR"   # file:// 경로를 상대경로로 쓰기 위함 (Git Bash 경로 변환 문제 회피)

PROJECT=task7
VPC_CIDR=10.0.0.0/16
SUBNET_CIDR=10.0.1.0/24
AZ=${AZ:-ap-northeast-2a}
INSTANCE_TYPE=${INSTANCE_TYPE:-t3.micro}
VOLUME_SIZE=8
KEY_NAME=${KEY_NAME:-task7-key}
KEY_FILE="$ROOT_DIR/${KEY_NAME}.pem"
AMI_PARAM=/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id

# Windows(Git Bash)의 aws.exe 는 CRLF 로 출력 → ID 끝의 \r 제거
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

log()  { printf '\033[36m[provision]\033[0m %s\n' "$*"; }
save() { echo "$1=$2" >> "$STATE_FILE"; }
tag()  { echo "ResourceType=$1,Tags=[{Key=Name,Value=$2},{Key=Project,Value=$PROJECT}]"; }

if [ -f "$STATE_FILE" ]; then
  echo "이미 $STATE_FILE 이 존재합니다. 먼저 cleanup.sh 를 실행하거나 파일을 확인하세요." >&2
  exit 1
fi

log "자격증명 확인"
aws sts get-caller-identity --query '{Account:Account,Arn:Arn}' --output table

MY_IP=${MY_IP:-$(curl -s https://checkip.amazonaws.com | tr -d '[:space:]')}
[[ "$MY_IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "내 IP 조회 실패: '$MY_IP'" >&2; exit 1; }
log "SSH 허용 IP: ${MY_IP}/32"

: > "$STATE_FILE"
save CREATED_AT "$(date '+%Y-%m-%dT%H:%M:%S')"
save MY_IP "$MY_IP"

# --- 1. VPC --------------------------------------------------------------------
VPC_ID=$(aws ec2 create-vpc --cidr-block "$VPC_CIDR" \
  --tag-specifications "$(tag vpc task7-vpc)" --query 'Vpc.VpcId' --output text)
save VPC_ID "$VPC_ID"
aws ec2 wait vpc-available --vpc-ids "$VPC_ID"
aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames '{"Value":true}'
log "VPC            $VPC_ID ($VPC_CIDR)"

# --- 2. Public Subnet ----------------------------------------------------------
SUBNET_ID=$(aws ec2 create-subnet --vpc-id "$VPC_ID" --cidr-block "$SUBNET_CIDR" \
  --availability-zone "$AZ" --tag-specifications "$(tag subnet task7-public-subnet)" \
  --query 'Subnet.SubnetId' --output text)
save SUBNET_ID "$SUBNET_ID"
aws ec2 modify-subnet-attribute --subnet-id "$SUBNET_ID" --map-public-ip-on-launch
log "Public Subnet  $SUBNET_ID ($SUBNET_CIDR, $AZ, 퍼블릭 IP 자동 할당)"

# --- 3. Internet Gateway -------------------------------------------------------
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications "$(tag internet-gateway task7-igw)" \
  --query 'InternetGateway.InternetGatewayId' --output text)
save IGW_ID "$IGW_ID"
aws ec2 attach-internet-gateway --internet-gateway-id "$IGW_ID" --vpc-id "$VPC_ID"
log "IGW            $IGW_ID (attached)"

# --- 4. Route Table: 0.0.0.0/0 → IGW -------------------------------------------
RTB_ID=$(aws ec2 create-route-table --vpc-id "$VPC_ID" \
  --tag-specifications "$(tag route-table task7-public-rt)" \
  --query 'RouteTable.RouteTableId' --output text)
save RTB_ID "$RTB_ID"
aws ec2 create-route --route-table-id "$RTB_ID" \
  --destination-cidr-block 0.0.0.0/0 --gateway-id "$IGW_ID" >/dev/null
RTB_ASSOC_ID=$(aws ec2 associate-route-table --route-table-id "$RTB_ID" \
  --subnet-id "$SUBNET_ID" --query 'AssociationId' --output text)
save RTB_ASSOC_ID "$RTB_ASSOC_ID"
log "Route Table    $RTB_ID (0.0.0.0/0 → $IGW_ID, subnet 연결)"

# --- 5. Security Group ---------------------------------------------------------
SG_ID=$(aws ec2 create-security-group --group-name task7-web-sg \
  --description "Task7 web: HTTP from anywhere, SSH from my IP only" \
  --vpc-id "$VPC_ID" --tag-specifications "$(tag security-group task7-web-sg)" \
  --query 'GroupId' --output text)
save SG_ID "$SG_ID"
aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --ip-permissions \
  "IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges=[{CidrIp=0.0.0.0/0,Description=HTTP-public}]" \
  "IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges=[{CidrIp=${MY_IP}/32,Description=SSH-my-ip-only}]" >/dev/null
log "Security Group $SG_ID (80←0.0.0.0/0, 22←${MY_IP}/32)"

# --- 6. Key Pair ---------------------------------------------------------------
if [ -f "$KEY_FILE" ]; then
  echo "키 파일 $KEY_FILE 이 이미 있습니다. 덮어쓰지 않도록 중단합니다." >&2; exit 1
fi
aws ec2 create-key-pair --key-name "$KEY_NAME" --key-type ed25519 \
  --tag-specifications "$(tag key-pair "$KEY_NAME")" \
  --query 'KeyMaterial' --output text > "$KEY_FILE"
chmod 400 "$KEY_FILE"
save KEY_NAME "$KEY_NAME"
log "Key Pair       $KEY_NAME → $KEY_FILE (재발급 불가, 안전 보관 / Git 커밋 금지)"

# --- 7. EC2 --------------------------------------------------------------------
# Git Bash(MSYS)는 "/aws/..." 로 시작하는 인자를 "C:/Program Files/Git/aws/..." 로 바꿔 버린다 → 변환 끄기
AMI_ID=$(MSYS_NO_PATHCONV=1 aws ssm get-parameter --name "$AMI_PARAM" --query 'Parameter.Value' --output text)
log "AMI            $AMI_ID (Ubuntu 24.04 LTS)"

INSTANCE_ID=$(aws ec2 run-instances \
  --image-id "$AMI_ID" --instance-type "$INSTANCE_TYPE" --key-name "$KEY_NAME" \
  --subnet-id "$SUBNET_ID" --security-group-ids "$SG_ID" \
  --associate-public-ip-address \
  --block-device-mappings "DeviceName=/dev/sda1,Ebs={VolumeSize=${VOLUME_SIZE},VolumeType=gp3,DeleteOnTermination=true}" \
  --metadata-options "HttpTokens=required,HttpEndpoint=enabled" \
  --user-data "file://scripts/setup-server.sh" \
  --tag-specifications "$(tag instance task7-web)" "$(tag volume task7-web-root)" \
  --query 'Instances[0].InstanceId' --output text)
save INSTANCE_ID "$INSTANCE_ID"
log "EC2            $INSTANCE_ID ($INSTANCE_TYPE) 부팅 대기..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID"

PUBLIC_IP=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
save PUBLIC_IP "$PUBLIC_IP"

# --- 8. 웹 서버 기동 대기 (user-data 실행 시간) --------------------------------
log "Nginx 기동 대기 (최대 5분)..."
for i in $(seq 1 30); do
  if [ "$(curl -s -m 5 "http://${PUBLIC_IP}/health")" = "OK" ]; then
    log "/health → OK"; break
  fi
  sleep 10
done

cat <<EOF

================ 생성 완료 ================
 Public IP : ${PUBLIC_IP}
 웹        : http://${PUBLIC_IP}
 헬스체크  : http://${PUBLIC_IP}/health
 SSH       : ssh -i ${KEY_NAME}.pem ubuntu@${PUBLIC_IP}
 상태 파일 : infra/state.env  (정리 시 bash infra/cleanup.sh)
===========================================
⚠️  실습이 끝나면 반드시 cleanup.sh 를 실행하세요.
EOF
