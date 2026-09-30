# 리소스 정리 체크리스트

> 실습 종료 후 이 순서대로 정리하고, 각 항목의 **근거(명령 출력 또는 콘솔 스크린샷)** 를 남긴다.
> 리전은 반드시 **서울(ap-northeast-2)** 로 맞춘 상태에서 확인한다.

- 정리 일시: `2026-09-30` (KST)
- 정리 방법: ☐ `bash infra/cleanup.sh` (자동)  ☑ 콘솔 수동

---

## 왜 이 순서인가?

리소스끼리 서로 **참조(의존)** 하고 있어서, 참조하는 쪽부터 지워야 삭제가 된다.

```text
EC2 ─ 사용 중 → EBS, Security Group, Subnet, (Elastic IP)
Subnet ─ 연결 → Route Table
Route Table ─ 경로 → IGW
IGW ─ 연결 → VPC
```

→ **EC2 → EBS → EIP → SG/Key Pair → Route Table → IGW → Subnet → VPC** 순으로 삭제

## 과금 위험도

| 리소스 | 남아 있으면 | 비고 |
|---|---|---|
| EC2 (running) | 시간당 과금 | 프리티어 월 750시간 초과 시 과금 |
| EC2 (stopped) | 인스턴스 요금은 없음 | **EBS 요금은 계속 발생** → Stop이 아니라 **Terminate** |
| EBS 볼륨 | GB·월 과금 | 인스턴스 종료 후 `available` 상태로 남는 볼륨 주의 |
| Elastic IP | 할당만 해도 과금 | 퍼블릭 IPv4는 사용 여부와 무관하게 시간당 과금 → **Release** |
| NAT Gateway / ALB / RDS | 시간당 과금 (고액) | 이번 실습에서 만들지 않았어도 한 번 확인 |
| VPC / Subnet / RT / IGW / SG | 무료 | 과금은 없지만 정리 대상(요구사항) |

---

## 체크리스트

| # | 항목 | 확인 방법 (콘솔 / CLI) | 기대 결과 | 완료 | 근거 |
|---|---|---|---|---|---|
| 1 | **EC2 인스턴스 Terminated** | EC2 → Instances / `aws ec2 describe-instances --filters Name=tag:Project,Values=task7 --query "Reservations[].Instances[].State.Name"` | `terminated` (1시간 후 목록에서 사라짐) | ☑ | `screenshots/cleanup-ec2-confirm.png`, `screenshots/cleanup-ec2.png` (종료됨) |
| 2 | **EBS 볼륨 삭제** (미사용 포함) | EC2 → Volumes / `aws ec2 describe-volumes --query "Volumes[].[VolumeId,State]"` | 목록 비어 있음 | ☑ | `screenshots/cleanup-volume.png` (현재 이 리전에 볼륨이 없습니다) |
| 3 | **Elastic IP Release** (할당했다면) | EC2 → Elastic IPs / `aws ec2 describe-addresses` | 목록 비어 있음 | ☑ (할당 안 함) | `screenshots/cleanup-탄력적ip.png` (이 리전에서 탄력적 IP 주소를 찾을 수 없음) |
| 4 | Key Pair 삭제 | EC2 → Key Pairs | task7-key 없음 | ☑ | `screenshots/cleanup-keypair.png` (1개의 키 페어 삭제 완료 · 표시할 키 페어 없음) |
| 5 | Security Group 삭제 | EC2 → Security Groups | task7-web-sg 없음 (default만 남음) | ☑ | `screenshots/cleanup-sg.png` (task7-web-sg 삭제됨 · 각 VPC의 default만 남음) |
| 6 | Route Table 삭제 | VPC → Route Tables | task7-public-rt 없음 | ☑ | `screenshots/B1-cleanup-rt.png` (서브넷 연결 해제) → `B2-cleanup-rt.png` (삭제 확인) → `cleanup-rt.png` (task7-public-rt 삭제 완료) |
| 7 | **Internet Gateway Detach + 삭제** | VPC → Internet Gateways / `aws ec2 describe-internet-gateways --filters Name=tag:Project,Values=task7` | 목록 비어 있음 | ☑ | `screenshots/B1-cleanup-igw.png`, `B2-cleanup-igw.png` (분리/삭제 과정) → `cleanup-igw.png` (igw-0e2a1faedc86eb077 삭제됨 · 기본 VPC의 IGW만 남음) |
| 8 | Subnet 삭제 | VPC → Subnets | task7-public-subnet 없음 | ☑ | `screenshots/B1-cleanup-subnet.png` (삭제 확인) → `cleanup-subnet.png` (subnet-023ecedbf31fd455e 삭제 완료 · 기본 VPC 서브넷 4개만 남음) |
| 9 | **VPC 삭제** | VPC → Your VPCs / `aws ec2 describe-vpcs --filters Name=tag:Project,Values=task7` | 목록 비어 있음 (default VPC만 남음) | ☑ | `screenshots/B1-cleanup-vpc.png` (대상 선택) → `B2-cleanup-vpc.png` (삭제 확인) → `cleanup-vpc.png` (task7-vpc 삭제 완료 · 기본 VPC `172.31.0.0/16` 만 남음) |
| 10 | (해당 시) NAT Gateway 삭제 | VPC → NAT Gateways | 없음 / `deleted` | ☑ N/A (생성 안 함) | |
| 11 | (해당 시) ELB/ALB 삭제 | EC2 → Load Balancers | 없음 | ☑ N/A (생성 안 함) | |
| 12 | (해당 시) RDS 삭제 | RDS → Databases | 없음 | ☑ N/A (생성 안 함) | |
| 13 | (권장) **Billing Dashboard 확인** | Billing and Cost Management → Bills / Free Tier | 예상 과금 $0, 프리티어 한도 내 | ☑ | `screenshots/cleanup-billing.png` (루트 계정 · 2026년 9월 청구서 **예상 총합계 USD 0.00** · 무료 플랜 — 요금 청구 없음) |
| 14 | 로컬 정리 | `task7-key.pem` 삭제 또는 안전 보관, `infra/state.env*` 확인 | 키 파일 Git 미포함 | ☑ | AWS 키 페어 삭제로 `task7-key.pem` 은 무효 · `.gitignore` 에 `*.pem`, `*credentials*.csv` 등록 → Git 미포함 · `infra/state.env*` 없음(콘솔로 진행) |

> 💡 콘솔에서 VPC 삭제 시 "Delete VPC" 는 연결된 Subnet·RT·IGW·SG 를 함께 삭제해 준다. 단, **EC2가 남아 있으면 삭제되지 않으므로** 1번을 먼저 완료할 것.
> 💡 Billing 화면은 IAM 사용자에게 결제 조회 권한이 없으면 보이지 않는다. 이 경우 관리 계정(또는 결제 조회 권한이 있는 사용자)으로 확인한다.

---

## 정리 결과 요약 (콘솔 수동 · 2026-09-30)

> `infra/cleanup.sh` 는 사용하지 않고 콘솔에서 수동으로 정리했다. 각 단계의 근거는 위 표의 스크린샷 참고.

| 리소스 | task7 잔존 | 확인 화면에 남은 것 (정상) |
|---|---|---|
| EC2 `task7-web` | **0** (종료됨) | — |
| EBS 볼륨 (리전 전체) | **0** | "현재 이 리전에 볼륨이 없습니다" |
| Elastic IP (리전 전체) | **0** | "탄력적 IP 주소를 찾을 수 없음" |
| Key Pair `task7-key` | **0** | "표시할 키 페어 없음" |
| Security Group `task7-web-sg` | **0** | 기본 VPC의 `default` SG |
| Route Table `task7-public-rt` | **0** | 기본 VPC의 main RT |
| Internet Gateway `task7-igw` | **0** | 기본 VPC의 IGW |
| Subnet `task7-public-subnet` | **0** | 기본 VPC 서브넷 4개 (`172.31.x.x/20`) |
| VPC `task7-vpc` | **0** | 기본 VPC `172.31.0.0/16` |
| NAT GW / ALB / RDS | 생성 안 함 | — |

→ **과금 위험 항목 없음.** Billing 청구서(2026년 9월) 예상 총합계 **USD 0.00** 확인. 기본 VPC 관련 리소스는 AWS 계정 생성 시 기본 제공되는 것으로, 과금이 없고 정리 대상이 아니다.
