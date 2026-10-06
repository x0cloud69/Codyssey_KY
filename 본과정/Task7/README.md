# Task7 — AWS VPC 기반 웹 서비스 인프라

VPC로 격리된 네트워크(Public Subnet + IGW + Route Table)에 EC2(Nginx) 웹 서버를 배포하고,
보안 그룹·IAM 최소권한을 적용한 뒤 외부 접속 검증 · 트러블슈팅 · 리소스 정리까지 수행한다.

## 외부 접속 검증

| 항목 | 내용 |
|---|---|
| **선택 방식** | **(B) `GET http://3.36.131.116/health`** → `200 OK` + 고정 응답 `OK` |
| 접속 정보 | `http://3.36.131.116/health` (실습 당시 퍼블릭 IP · 리소스 정리 후에는 접속 불가) |
| 참고 | 같은 서버에서 `http://3.36.131.116/` 접속 시 "Hello Cloud" 페이지도 표시됨 |
| 증빙 | ![외부 접속 결과](docs/screenshots/external-health.png) |

```text
$ curl -i http://3.36.131.116/health
HTTP/1.1 200 OK
Server: nginx/1.24.0 (Ubuntu)
Content-Type: text/plain

OK
```

**증빙 스크린샷**

| (B) 선택 방식 — 내 PC `curl.exe -i /health` | 브라우저 `http://3.36.131.116/health` |
|---|---|
| ![외부 접속 - curl](docs/screenshots/external-health.png) | ![외부 접속 - health](docs/screenshots/7.Health.png) |

**참고 — 브라우저 `http://3.36.131.116/` (Hello Cloud 페이지)**

![외부 접속 - Hello Cloud](docs/screenshots/7.Hello%20Cloud.png)

---

## 제출물

| 결과물 | 경로 |
|---|---|
| 아키텍처 다이어그램 | [`docs/architecture.png`](docs/architecture.png) |
| 외부 접속 증빙 | 이 README + `docs/screenshots/external-health.png` |
| 트러블슈팅 보고서 | [`docs/troubleshooting.md`](docs/troubleshooting.md) |
| 리소스 정리 체크리스트 | [`docs/cleanup-checklist.md`](docs/cleanup-checklist.md) |

![architecture](docs/architecture.png)

### 🔎 다이어그램 읽는 법 — 요청이 처리되는 순서

다이어그램에는 **세 가지 흐름**이 있다. 선 색으로 구분한다.

| 선 | 흐름 | 누가 → 어디로 | 포트 |
|---|---|---|---|
| **파랑 실선** | A. 웹 서비스 접속 | 인터넷 사용자 → EC2 | HTTP `80` |
| **주황 점선** | B. 서버 관리 접속 | 학습자 PC → EC2 | SSH `22` |
| **초록 점선** | C. 서버의 외부 통신 | EC2 → 인터넷 | 전체 (아웃바운드) |

#### A. 🌐 인터넷 사용자 — 웹 페이지 보기 (`http://3.36.131.116/health`)

| 순서 | 위치 | 무슨 일이 일어나나 | 비유 |
|---|---|---|---|
| ① | **인터넷 사용자** (브라우저 / curl) | 주소창에 `http://3.36.131.116/health` 입력 → **80번 포트**로 요청 출발. 누구나(모든 IP) 가능 | 손님이 도로명 주소를 보고 출발 |
| ② | **Internet Gateway** `task7-igw` | VPC 정문 통과. 외부 주소(퍼블릭 IP `3.36.131.116`)를 내부 주소(프라이빗 IP `10.0.1.173`)로 **변환** | 정문 경비가 "몇 동 몇 호" 로 안내 |
| ③ | **Route Table** `task7-public-rt` | `10.0.0.0/16 → local` 규칙으로 VPC 안쪽 목적지로 전달 (`0.0.0.0/0 → IGW` 가 있어 이 서브넷이 **퍼블릭**) | 단지 안 길 안내 표지판 |
| ④ | **Public Subnet** `task7-public-subnet` | `10.0.1.0/24` 구역(ap-northeast-2a) 안으로 진입 | 해당 **동** 도착 |
| ⑤ | **Security Group** `task7-web-sg` | 인바운드 규칙 확인 → **`80 ← 0.0.0.0/0` 허용** 이므로 통과 (허용 안 된 포트는 여기서 차단) | 현관 **도어락** 통과 |
| ⑥ | **EC2** `task7-web` · **Nginx :80** | Nginx가 요청 처리 → `/health` 면 `OK`, `/` 면 Hello Cloud 페이지 생성 | 집주인이 문 열고 응답 |
| ⑦ | **응답 복귀** | `200 OK` + `OK` 가 **왔던 길을 거꾸로** (SG → Subnet → IGW → 인터넷) 돌아감. SG는 **상태 저장(stateful)** 이라 응답용 규칙이 따로 필요 없음 | 같은 길로 답장 배달 |

> 요약: **사용자 → IGW → Route Table → Subnet → SG(80 허용) → EC2 Nginx → (응답) 역순 복귀**
> 하나라도 빠지면(퍼블릭 IP 없음 · IGW 미연결 · 경로 없음 · SG 80 미허용 · Nginx 중지) **타임아웃 또는 연결 거부**가 난다.

#### B. 💻 학습자 PC — 서버 관리 접속 (`ssh -i task7-key.pem ubuntu@3.36.131.116`)

| 순서 | 위치 | 무슨 일이 일어나나 |
|---|---|---|
| ① | **학습자 PC** (내 공인 IP `x.x.x.x`) | `ssh` / `scp` 명령 실행 → **22번 포트**로 요청. 개인키 `task7-key.pem` 준비 |
| ② | **Internet Gateway** | A와 같은 정문 통과 · 주소 변환 |
| ③ | **Route Table → Public Subnet** | A와 같은 경로로 서브넷 진입 |
| ④ | **Security Group** | 인바운드 규칙 **`22 ← 내 IP/32`** 확인 → **내 PC에서 온 요청만 통과**, 다른 IP는 전부 차단 |
| ⑤ | **EC2** (SSH 서버) | 키 확인 — EC2에 등록된 **공개키(자물쇠)** 와 내 **개인키(열쇠)** 가 짝이 맞으면 로그인 성공 → `ubuntu@ip-10-0-1-173:~$` |
| ⑥ | **작업** | 원격 터미널에서 `bash verify-instance.sh` 등 실행 → 결과가 같은 길로 내 화면에 표시 |

> 요약: **내 PC → IGW → Subnet → SG(22, 내 IP만) → EC2 키 인증 → 원격 터미널**
> 웹(80)은 **누구나**, 관리(22)는 **나만** — 이것이 SG 최소권한 설계의 핵심.

#### C. 🔁 EC2 → 인터넷 — 서버가 밖으로 나가는 통신 (아웃바운드)

| 순서 | 위치 | 무슨 일이 일어나나 |
|---|---|---|
| ① | **EC2** | 서버가 스스로 외부 요청 시작 — 최초 부팅 시 `apt install nginx`, 점검 시 `curl https://example.com` |
| ② | **Security Group** | 아웃바운드 규칙 **`all → 0.0.0.0/0`** (기본값) 이므로 통과 |
| ③ | **Route Table** | 목적지가 VPC 밖(`0.0.0.0/0`) → **IGW로 보냄** |
| ④ | **Internet Gateway → 인터넷** | 프라이빗 IP를 퍼블릭 IP로 변환해 인터넷으로 나감 → 응답 수신 (`HTTP/2 200`) |

> 요약: **EC2 → SG(아웃바운드 허용) → Route Table(0.0.0.0/0 → IGW) → IGW → 인터넷**
> 이 경로가 있어야 패키지 설치·업데이트가 가능하다 (`verify-instance.sh` 첫 번째 PASS 항목).

## 폴더 구조

```text
Task7/
├── README.md
├── 문제.md                              # 과제 원문 정리
├── docs/
│   ├── aws-setup.md                     # 0단계: AWS 계정·IAM·도구 준비
│   ├── architecture.png                 # 아키텍처 다이어그램
│   ├── troubleshooting.md               # 트러블슈팅 보고서
│   ├── cleanup-checklist.md             # 리소스 정리 체크리스트
│   └── screenshots/                     # 증빙 스크린샷 저장 위치
├── iam/
│   └── task7-least-privilege-policy.json  # IAM 최소권한 정책
├── scripts/
│   ├── setup-server.sh                  # EC2 user-data: Nginx + / + /health
│   ├── verify-instance.sh               # EC2 내부 점검 (아웃바운드/localhost 200/health)
│   ├── verify-external.ps1              # 내 PC(Windows) 외부 접속 검증
│   └── verify-external.sh               # 내 PC(macOS/Linux/Git Bash) 외부 접속 검증
└── infra/
    ├── provision.sh                     # AWS CLI로 전체 인프라 생성
    └── cleanup.sh                       # 역순 삭제 + 잔존 리소스 검증
```

---

## 구성 요약

| 구분 | 설정 |
|---|---|
| 리전 | `ap-northeast-2` (서울) |
| VPC | `task7-vpc` · `10.0.0.0/16` · DNS hostnames 활성화 |
| Public Subnet | `task7-public-subnet` · `10.0.1.0/24` · `ap-northeast-2a` · 퍼블릭 IP 자동 할당 |
| Internet Gateway | `task7-igw` · VPC에 Attach |
| Route Table | `task7-public-rt` · `0.0.0.0/0 → IGW` · Public Subnet 연결 |
| Security Group | `task7-web-sg` · IN `80 ← 0.0.0.0/0` · IN `22 ← 내 IP/32` · (전체 포트 허용 규칙 없음) |
| EC2 | `task7-web` · `t3.micro` · Ubuntu 24.04 LTS · EBS gp3 8GiB (종료 시 삭제) · IMDSv2 필수 |
| 웹 서버 | Nginx · `GET /` → Hello Cloud 페이지 · `GET /health` → `200 OK` |
| IAM | 사용자 `task7-user` 1명 · 정책 `Task7LeastPrivilege` (EC2/VPC/SG 한정, 서울 리전 한정) |

---

## 📖 약어 정리 (Full Name)

| 약어 | Full Name | 한 줄 뜻 |
|---|---|---|
| **AWS** | Amazon Web Services | 아마존의 클라우드 서비스 |
| **IAM** | Identity and Access Management | 사용자·권한(출입증) 관리 |
| **MFA** | Multi-Factor Authentication | 비밀번호 + 인증 앱 코드로 이중 확인 |
| **VPC** | Virtual Private Cloud | 나만의 격리된 가상 네트워크 |
| **CIDR** | Classless Inter-Domain Routing | `10.0.0.0/16` 처럼 IP 범위를 표기하는 방식 |
| **AZ** | Availability Zone | 리전 안의 물리적으로 분리된 데이터센터 |
| **IGW** | Internet Gateway | VPC ↔ 인터넷 출입구 |
| **RT** | Route Table | 트래픽 경로 규칙표 |
| **SG** | Security Group | 인스턴스 단위 가상 방화벽 |
| **NACL** | Network Access Control List | 서브넷 단위 방화벽 (이번 실습은 기본값 사용) |
| **NAT** | Network Address Translation | 사설 IP ↔ 공인 IP 주소 변환 (NAT Gateway는 이번 실습에서 미사용) |
| **EC2** | Elastic Compute Cloud | 가상 서버(컴퓨터) |
| **AMI** | Amazon Machine Image | EC2에 설치할 OS 이미지 |
| **EBS** | Elastic Block Store | EC2용 가상 디스크 |
| **gp3** | General Purpose SSD (3세대) | 범용 SSD 볼륨 유형 |
| **SSD** | Solid State Drive | 반도체 저장장치 |
| **EIP** | Elastic IP | 고정 퍼블릭 IP (이번 실습에서 미사용) |
| **IMDS** | Instance Metadata Service | 인스턴스가 자기 정보를 조회하는 내부 서비스 (v2 = 토큰 필수) |
| **vCPU** | virtual Central Processing Unit | 가상 CPU(중앙처리장치) |
| **GiB** | Gibibyte | 2³⁰ 바이트 (≈ 1.07 GB) |
| **OS** | Operating System | 운영체제 (Ubuntu 등) |
| **LTS** | Long Term Support | 장기 지원 버전 (Ubuntu 24.04 LTS) |
| **IP** | Internet Protocol | 인터넷 주소 체계 (IPv4 = 버전 4) |
| **DNS** | Domain Name System | 이름 → IP 주소 변환(인터넷 전화번호부) |
| **TCP** | Transmission Control Protocol | 신뢰성 있는 데이터 전송 규약 (HTTP·SSH가 사용) |
| **HTTP / HTTPS** | HyperText Transfer Protocol (Secure) | 웹 통신 규약 / 암호화된 웹 통신 |
| **URL** | Uniform Resource Locator | 웹 주소 (`http://…/health`) |
| **SSH** | Secure Shell | 암호화된 원격 터미널 접속 |
| **scp** | Secure Copy Protocol | SSH 기반 파일 복사 |
| **curl** | Client URL | 명령줄 HTTP 요청 도구 |
| **CLI** | Command Line Interface | 명령어로 조작하는 방식 (AWS CLI) |
| **JSON** | JavaScript Object Notation | IAM 정책 등을 적는 데이터 형식 |
| **ARN** | Amazon Resource Name | AWS 리소스의 고유 식별 이름 |
| **ALB / ELB** | Application / Elastic Load Balancer | 트래픽 분산 장치 (이번 실습에서 미사용) |
| **RDS** | Relational Database Service | 관리형 데이터베이스 (이번 실습에서 미사용) |
| **KST / UTC** | Korea Standard Time / Coordinated Universal Time | 한국 표준시(UTC+9) / 세계 표준시 |

---

## 진행 절차

### 0단계. AWS 환경 구축 (계정이 없다면 여기부터)

👉 **[`docs/aws-setup.md`](docs/aws-setup.md)** 를 따라 진행한다.

| 순서 | 내용 | 사용 계정 |
|---|---|---|
| A | AWS 계정 가입 (Free plan) | 루트 |
| B | 루트 계정 MFA 설정 | 루트 |
| C | 과금 알림 (Zero spend budget) | 루트 |
| D | IAM 정책 `Task7LeastPrivilege` + 사용자 `task7-user` 생성 | 루트 |
| E | `task7-user` 로 로그인, 서울 리전 선택 | **task7-user (이후 계속)** |
| F | 내 PC 도구 확인 (SSH, CLI는 선택) | — |

### 1단계. IAM 최소권한 확인

> 💡 **개념 — IAM이란?**
> **IAM(Identity and Access Management)** 은 AWS 계정 안에서 **"누가 · 무엇을 · 어디까지"** 할 수 있는지 정하는 **출입증 시스템**이다.
> - **루트 계정** = 건물주 마스터키. 모든 걸 할 수 있어 위험하므로 평소엔 금고에 보관(MFA(Multi-Factor Authentication, 다중 인증) 걸고 사용 최소화).
> - **IAM 사용자** (`task7-user`) = 직원 출입증. 필요한 방(EC2 · VPC · SG)만 열 수 있게 발급.
> - **정책(Policy)** = 출입증에 적힌 허용 목록(JSON, JavaScript Object Notation 형식). 목록에 없으면 기본 **거부**.
> - **최소권한 원칙** = "필요한 만큼만" 준다. 출입증을 잃어버려도 피해가 작다.

> 루트 계정은 0단계 초기 설정(계정 보안·IAM 사용자 생성)에만 사용하고, 실습은 `task7-user` 로만 진행한다.

- `task7-user` 에 연결된 정책이 `Task7LeastPrivilege` **1개뿐**인지 확인 (`AdministratorAccess` 없음) → 캡처 `docs/screenshots/iam-policy_1.png`, `iam-policy_2.png`
- 정책 원본: [`iam/task7-least-privilege-policy.json`](iam/task7-least-privilege-policy.json) — 생성 방법은 [`docs/aws-setup.md`](docs/aws-setup.md) D 참고

**정책 설계 포인트**

| Statement | 허용/거부 | 이유 |
|---|---|---|
| `ReadOnlyEc2VpcInSeoul` | `ec2:Describe*` 등 조회 | 콘솔 화면 표시에 필요 |
| `NetworkVpcSubnetIgwRoute` | VPC/Subnet/IGW/Route 생성·연결·삭제 | 네트워크 구성 |
| `SecurityGroup` | SG 생성·규칙 추가/삭제 | 접근 제어 |
| `ComputeInstanceKeyVolumeEip` | 인스턴스·키페어·볼륨·EIP·태그 | 컴퓨트 및 정리 |
| `ResolvePublicAmiIdsFromSsm` | AWS 공개 AMI 파라미터 조회만 | 최신 Ubuntu AMI 조회 |
| `DecodeIamDenyMessages…` | 권한 오류 메시지 디코딩 | 트러블슈팅 근거 확보 |
| `DenyNonFreeTierInstanceTypes` | **거부**: `t2/t3.micro` 외 타입 | 과금 방지 |
| `DenyLargeVolumes` | **거부**: 10GiB 초과 볼륨 | 과금 방지 |
| (공통 조건) | `aws:RequestedRegion = ap-northeast-2` | 서울 외 리전 사용 차단 |
| (없음) | S3 / RDS / IAM 등 | 실습과 무관 → 부여하지 않음 |

<details>
<summary>📘 규칙 풀이 — 쉽게 이해하기 (클릭)</summary>
<p>정책 = <strong><code>task7-user</code> 출입증에 &quot;어느 방을 열 수 있는지&quot; 적어 둔 규칙표</strong></p>
<p><strong>먼저 알아둘 기본 규칙</strong></p>
<table>
<thead>
<tr>
<th>규칙</th>
<th>뜻</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>목록에 없으면 거부</strong></td>
<td><code>Allow</code> 로 적힌 것만 가능. 안 적힌 건 자동 차단 (암묵적 거부)</td>
</tr>
<tr>
<td><strong>Deny가 이긴다</strong></td>
<td>어딘가에 허용이 있어도 <strong><code>Deny</code> 가 하나라도 걸리면 무조건 차단</strong></td>
</tr>
</tbody>
</table>
<p><strong>8개 규칙 풀이</strong></p>
<table>
<thead>
<tr>
<th>#</th>
<th>Statement</th>
<th>종류</th>
<th>쉬운 설명</th>
<th>비유</th>
</tr>
</thead>
<tbody>
<tr>
<td>①</td>
<td><code>ReadOnlyEc2VpcInSeoul</code></td>
<td>허용</td>
<td><code>ec2:Describe*</code> = EC2·VPC·서브넷 등을 <strong>조회만</strong>. 없으면 콘솔 화면이 텅 빔</td>
<td>건물 <strong>안내도 열람</strong></td>
</tr>
<tr>
<td>②</td>
<td><code>NetworkVpcSubnetIgwRoute</code></td>
<td>허용</td>
<td>VPC·서브넷·IGW·라우팅 테이블 <strong>생성·연결·삭제</strong> (2단계 1~4번, 5단계 정리)</td>
<td>단지·동·정문·표지판 <strong>공사 허가증</strong></td>
</tr>
<tr>
<td>③</td>
<td><code>SecurityGroup</code></td>
<td>허용</td>
<td>보안 그룹 생성, 인바운드/아웃바운드 규칙 추가·삭제</td>
<td><strong>도어락 설치·비밀번호 변경</strong></td>
</tr>
<tr>
<td>④</td>
<td><code>ComputeInstanceKeyVolumeEip</code></td>
<td>허용</td>
<td>EC2 시작·중지·종료, 키 페어 생성·삭제, 볼륨 삭제, 탄력적 IP 할당·반납, 태그</td>
<td><strong>집 짓기·열쇠 발급·철거</strong></td>
</tr>
<tr>
<td>⑤</td>
<td><code>ResolvePublicAmiIdsFromSsm</code></td>
<td>허용</td>
<td>AWS 공개 &quot;최신 Ubuntu 이미지 ID&quot; 만 조회 (<code>/aws/service/*</code> 경로 한정)</td>
<td><strong>공식 설치 CD 목록 열람</strong></td>
</tr>
<tr>
<td>⑥</td>
<td><code>DecodeIamDenyMessages…</code></td>
<td>허용</td>
<td>권한 오류 시 받는 암호 같은 문자열을 <strong>&quot;어떤 규칙에 막혔는지&quot;</strong> 해독 → 트러블슈팅 근거</td>
<td><strong>출입 거부 사유서 열람</strong></td>
</tr>
<tr>
<td>⑦</td>
<td><code>DenyNonFreeTierInstanceTypes</code></td>
<td><strong>거부</strong></td>
<td><code>t2.micro</code>·<code>t3.micro</code> <strong>외</strong> 유형으로 EC2 생성 차단 → 비싼 서버 실수 원천 봉쇄</td>
<td><strong>&quot;원룸만, 펜트하우스 금지&quot;</strong></td>
</tr>
<tr>
<td>⑧</td>
<td><code>DenyLargeVolumes</code></td>
<td><strong>거부</strong></td>
<td><strong>10GiB 초과</strong> 디스크 생성 차단 → 용량 과금 사고 방지</td>
<td><strong>&quot;창고는 10평까지만&quot;</strong></td>
</tr>
</tbody>
</table>
<p><strong>공통 조건 — 서울만</strong>
①~④ 에 <code>aws:RequestedRegion = ap-northeast-2</code> 조건 → <strong>서울 리전에서만</strong> 동작. 도쿄·미국 등 다른 리전에 몰래 리소스가 생겨 과금되는 것을 차단 (= <strong>&quot;서울 지점 전용 출입증&quot;</strong>)</p>
<p><strong>일부러 뺀 것</strong></p>
<table>
<thead>
<tr>
<th>빠진 권한</th>
<th>이유</th>
</tr>
</thead>
<tbody>
<tr>
<td>S3 · RDS · Lambda 등 다른 서비스</td>
<td>과제와 무관</td>
</tr>
<tr>
<td><strong>IAM 권한</strong></td>
<td>자기 권한을 스스로 늘리는 것(권한 상승)을 막기 위해 — <strong>가장 중요</strong></td>
</tr>
<tr>
<td>Compute Optimizer · Route 53 DNS 방화벽 등</td>
<td>불필요 → 콘솔에 빨간 권한 오류가 뜬 이유이자, <strong>정책이 제대로 동작한다는 증거</strong> (<a href="docs/troubleshooting.md">트러블슈팅 사례 2</a>)</td>
</tr>
</tbody>
</table>
<blockquote>
<p><strong>한 줄 요약</strong> — <strong>&quot;필요한 것(EC2·VPC·SG)만, 서울에서만, 싼 것만&quot;</strong> 할 수 있는 출입증. 유출되더라도 피해가 작고, 요금 폭탄이 날 수 없다.</p>
</blockquote>
</details>

### 2단계. 인프라 생성 — 둘 중 하나 선택

#### 방법 A. 콘솔 (권장: 과정을 눈으로 이해)

> 🏢 **한눈에 보는 비유 — AWS 네트워크 = 아파트 단지**
>
> | AWS 구성 요소 | 아파트 비유 | 한 줄 설명 |
> |---|---|---|
> | **VPC** | 아파트 **단지** 전체 | 나만 쓰는 격리된 사설 네트워크 |
> | **Subnet** | 단지 안의 **동(棟)** | VPC를 잘게 나눈 구역 (가용 영역 1곳에 위치) |
> | **Internet Gateway** | 단지 **정문** | VPC ↔ 인터넷 출입구 |
> | **Route Table** | 동 입구의 **길 안내 표지판** | "밖으로 가려면 정문으로" 같은 경로 규칙 |
> | **Security Group** | 각 세대 **현관 도어락** | 어떤 손님(IP·포트)을 들여보낼지 결정 |
> | **EC2** | 동 안의 **세대(집)** | 실제로 웹 서버가 돌아가는 가상 컴퓨터 |
> | **퍼블릭 IP / DNS** | 외부에서 찾아올 **도로명 주소** | 인터넷에서 이 서버를 찾아오는 주소 |

<details>
<summary><b>1단계 · VPC 생성</b> (클릭해서 펼치기)</summary>
<p><strong>VPC</strong> 생성: <code>task7-vpc</code>, <code>10.0.0.0/16</code> → Actions → Edit VPC settings → DNS hostnames 활성화</p>
<blockquote>
<p>💡 <strong>개념 — VPC와 DNS</strong></p>
<ul>
<li><strong>VPC(Virtual Private Cloud)</strong> = AWS 안에 만드는 <strong>나만의 격리된 네트워크</strong>. 다른 고객의 서버와 섞이지 않는 울타리 친 단지.</li>
<li><strong>CIDR(Classless Inter-Domain Routing) <code>10.0.0.0/16</code></strong> = 이 단지에서 쓸 <strong>사설 IP 주소 범위</strong>. <code>/16</code> 은 앞 16비트(<code>10.0</code>)가 고정 → <code>10.0.0.0 ~ 10.0.255.255</code>, 약 <strong>65,536개</strong> 주소.</li>
<li><strong>DNS(Domain Name System)</strong> = <strong>이름 → IP 주소 변환기</strong>(인터넷 전화번호부). 사람이 <code>google.com</code> 을 입력하면 DNS가 <code>142.250.x.x</code> 로 바꿔 준다.</li>
<li><strong>DNS resolution(확인)</strong> = VPC 안의 서버가 DNS 질문을 할 수 있게 함 (기본 ON).</li>
<li><strong>DNS hostnames(호스트 이름)</strong> = VPC 안의 서버에 <code>ec2-3-36-131-116.ap-northeast-2.compute.amazonaws.com</code> 같은 <strong>이름표를 붙여 줌</strong> → 이걸 켜야 EC2에 퍼블릭 DNS 이름이 생긴다.</li>
</ul>
</blockquote>
<details>
<summary>상세 절차 (클릭)</summary>
<p><strong>(0) 리전 확인</strong> — 콘솔 우측 상단 리전이 <strong>아시아 태평양(서울) <code>ap-northeast-2</code></strong> 인지 확인</p>
<p><strong>(1) VPC 생성</strong></p>
<ol>
<li>
<p>상단 검색창 <code>VPC</code> → <strong>VPC</strong> 서비스 → 왼쪽 <strong>Your VPCs(VPC)</strong> → <strong>Create VPC(VPC 생성)</strong></p>
</li>
<li>
<p>설정 입력</p>
<table>
<thead>
<tr>
<th>항목</th>
<th>값</th>
</tr>
</thead>
<tbody>
<tr>
<td>Resources to create (생성할 리소스)</td>
<td><strong>VPC only (VPC만)</strong></td>
</tr>
<tr>
<td>Name tag (이름 태그)</td>
<td><code>task7-vpc</code></td>
</tr>
<tr>
<td>IPv4 CIDR block</td>
<td>IPv4 CIDR manual input (수동 입력)</td>
</tr>
<tr>
<td>IPv4 CIDR</td>
<td><code>10.0.0.0/16</code></td>
</tr>
<tr>
<td>IPv6 CIDR block</td>
<td>No IPv6 CIDR block</td>
</tr>
<tr>
<td>Tenancy (테넌시)</td>
<td>Default (기본값)</td>
</tr>
</tbody>
</table>
</li>
<li>
<p><strong>Create VPC</strong> 클릭</p>
</li>
</ol>
<blockquote>
<p>⚠️ <em>VPC and more(VPC 등)</em> 를 선택하면 서브넷·라우팅 테이블·NAT 등이 자동 생성된다. 이후 단계에서 직접 만들므로 <strong>VPC only</strong> 선택.</p>
</blockquote>
<p><strong>(2) DNS hostnames 활성화</strong></p>
<ol>
<li><code>task7-vpc</code> 선택 → 우측 상단 <strong>Actions(작업)</strong> → <strong>Edit VPC settings(VPC 설정 편집)</strong></li>
<li>DNS settings
<ul>
<li>☑ Enable DNS resolution (DNS 확인 활성화) — 기본값으로 체크됨</li>
<li>☑ <strong>Enable DNS hostnames (DNS 호스트 이름 활성화)</strong> — <strong>체크</strong></li>
</ul>
</li>
<li><strong>Save(저장)</strong></li>
</ol>
<p><strong>(3) 확인</strong> — VPC <strong>Details</strong> 탭에서 <code>DNS hostnames: Enabled</code> 확인</p>
<blockquote>
<p>DNS hostnames 를 켜야 퍼블릭 IP를 받은 EC2에 <code>ec2-x-x-x-x.ap-northeast-2.compute.amazonaws.com</code> 형태의 퍼블릭 DNS 이름이 부여된다.</p>
</blockquote>
</details>
<p><strong>📸 증빙 캡처</strong></p>
<p><img width="100%" src="docs/screenshots/1.VPC.png" alt="VPC - 세부 정보 (DNS 호스트 이름 활성화됨)" /></p>
</details>

<details>
<summary><b>2단계 · Subnet 생성</b> (클릭해서 펼치기)</summary>
<p><strong>Subnet</strong> 생성: <code>task7-public-subnet</code>, <code>10.0.1.0/24</code>, <code>ap-northeast-2a</code> → Edit subnet settings → <em>Enable auto-assign public IPv4</em> 체크</p>
<blockquote>
<p>💡 <strong>개념 — Subnet · 가용 영역 · 퍼블릭 IP</strong></p>
<ul>
<li><strong>Subnet</strong> = VPC 주소 범위를 <strong>잘게 나눈 구역</strong>. <code>10.0.1.0/24</code> → <code>10.0.1.0 ~ 10.0.1.255</code> (256개 중 AWS 예약 5개 제외 <strong>251개</strong> 사용 가능).</li>
<li><strong>가용 영역(AZ, Availability Zone · <code>ap-northeast-2a</code>)</strong> = 서울 리전 안의 <strong>물리적으로 분리된 데이터센터</strong>. 서브넷은 AZ 하나에 속한다.</li>
<li><strong>퍼블릭 서브넷 vs 프라이빗 서브넷</strong> = 이름이 아니라 <strong>인터넷(IGW)으로 가는 길이 있느냐</strong>로 결정된다 (4번 Route Table 참고).</li>
<li><strong>프라이빗 IP vs 퍼블릭 IP (IP = Internet Protocol 주소)</strong> = 프라이빗(<code>10.0.1.173</code>)은 <strong>단지 내부 호수</strong>, 퍼블릭(<code>3.36.131.116</code>)은 <strong>외부 도로명 주소</strong>. <em>자동 할당</em>을 켜면 EC2가 생길 때 퍼블릭 IP가 자동으로 붙는다.</li>
</ul>
</blockquote>
<details>
<summary>상세 절차 (클릭)</summary>
<p><strong>(1) 서브넷 생성</strong></p>
<ol>
<li>
<p>VPC 콘솔 왼쪽 <strong>Subnets(서브넷)</strong> → <strong>Create subnet(서브넷 생성)</strong></p>
</li>
<li>
<p><strong>VPC ID</strong> 에서 <strong><code>task7-vpc</code></strong> 선택 (선택해야 아래 입력란이 나타남)</p>
</li>
<li>
<p>Subnet settings(서브넷 설정)</p>
<table>
<thead>
<tr>
<th>항목</th>
<th>값</th>
</tr>
</thead>
<tbody>
<tr>
<td>Subnet name (서브넷 이름)</td>
<td><code>task7-public-subnet</code></td>
</tr>
<tr>
<td>Availability Zone (가용 영역)</td>
<td>아시아 태평양(서울) / <code>ap-northeast-2a</code></td>
</tr>
<tr>
<td>IPv4 VPC CIDR block</td>
<td><code>10.0.0.0/16</code> (자동 선택)</td>
</tr>
<tr>
<td>IPv4 subnet CIDR block</td>
<td><code>10.0.1.0/24</code></td>
</tr>
</tbody>
</table>
</li>
<li>
<p><strong>Create subnet</strong> 클릭</p>
</li>
</ol>
<blockquote>
<p>⚠️ VPC ID를 기본 VPC(<code>172.31.0.0/16</code>)로 잘못 선택하는 실수가 가장 흔하다. 반드시 <code>task7-vpc</code> 확인.</p>
</blockquote>
<p><strong>(2) 퍼블릭 IPv4 자동 할당 활성화</strong></p>
<ol>
<li><code>task7-public-subnet</code> 선택 → <strong>Actions(작업)</strong> → <strong>Edit subnet settings(서브넷 설정 편집)</strong></li>
<li>Auto-assign IP settings → ☑ <strong>Enable auto-assign public IPv4 address (퍼블릭 IPv4 주소 자동 할당 활성화)</strong></li>
<li><strong>Save(저장)</strong></li>
</ol>
<p><strong>(3) 확인</strong> — 서브넷 <strong>세부 정보</strong> 탭</p>
<table>
<thead>
<tr>
<th>항목</th>
<th>기대값</th>
</tr>
</thead>
<tbody>
<tr>
<td>VPC</td>
<td><code>task7-vpc</code></td>
</tr>
<tr>
<td>IPv4 CIDR</td>
<td><code>10.0.1.0/24</code> (사용 가능 IP 251개 — /24 256개 중 AWS 예약 5개 제외)</td>
</tr>
<tr>
<td>가용 영역</td>
<td><code>apne2-az1 (ap-northeast-2a)</code></td>
</tr>
<tr>
<td>퍼블릭 IPv4 주소 자동 할당</td>
<td><strong>예</strong></td>
</tr>
<tr>
<td>기본 서브넷</td>
<td>아니요</td>
</tr>
</tbody>
</table>
<blockquote>
<ul>
<li>목록의 <strong>퍼블릭 액세스 차단: 끄기</strong> 는 자동 할당과 <strong>별개 설정</strong>이며 &quot;끄기&quot;가 정상이다.</li>
<li>목록의 <code>172.31.x.x/20</code> 서브넷 4개는 AWS 기본 VPC 소속이므로 건드리지 않는다.</li>
<li>서브넷의 가용 영역은 생성 후 변경할 수 없다(잘못 만들면 삭제 후 재생성).</li>
</ul>
</blockquote>
</details>
<p><strong>📸 증빙 캡처</strong></p>
<p><img width="100%" src="docs/screenshots/2.Subnet.png" alt="Subnet - 세부 정보 (퍼블릭 IPv4 자동 할당: 예)" /></p>
</details>

<details>
<summary><b>3단계 · Internet Gateway 생성 · 연결</b> (클릭해서 펼치기)</summary>
<p><strong>Internet Gateway</strong> 생성: <code>task7-igw</code> → Attach to VPC → <code>task7-vpc</code></p>
<blockquote>
<p>💡 <strong>개념 — IGW(Internet Gateway, 인터넷 게이트웨이)</strong></p>
<ul>
<li>VPC와 인터넷을 잇는 <strong>정문</strong>. IGW가 없으면 VPC는 외부와 완전히 단절된 섬이다.</li>
<li>퍼블릭 IP ↔ 프라이빗 IP <strong>주소 변환</strong>도 IGW가 처리한다 (밖에서 <code>3.36.131.116</code> 으로 오면 안에서 <code>10.0.1.173</code> 으로 전달).</li>
<li>정문을 <strong>만들기만</strong> 해서는 안 되고, VPC에 <strong>붙이고(Attach)</strong>, 다음 단계에서 <strong>길 안내(Route)</strong> 까지 해 줘야 통한다.</li>
</ul>
</blockquote>
<details>
<summary>상세 절차 (클릭)</summary>
<p><strong>(1) 인터넷 게이트웨이 생성</strong></p>
<ol>
<li>VPC 콘솔 왼쪽 <strong>Internet gateways(인터넷 게이트웨이)</strong> → <strong>Create internet gateway(인터넷 게이트웨이 생성)</strong></li>
<li>Name tag(이름 태그): <code>task7-igw</code></li>
<li><strong>Create internet gateway</strong> 클릭 → 이 시점 상태는 <strong>Detached</strong></li>
</ol>
<p><strong>(2) VPC에 연결 (Attach)</strong></p>
<ol>
<li>생성 직후 상단 초록 배너의 <strong>Attach to a VPC(VPC에 연결)</strong> 클릭
(배너를 놓쳤으면 <code>task7-igw</code> 선택 → <strong>Actions(작업)</strong> → <strong>Attach to VPC(VPC에 연결)</strong>)</li>
<li>Available VPCs(사용 가능한 VPC): <strong><code>task7-vpc</code></strong> 선택</li>
<li><strong>Attach internet gateway(인터넷 게이트웨이 연결)</strong> 클릭</li>
</ol>
<p><strong>(3) 확인</strong></p>
<table>
<thead>
<tr>
<th>항목</th>
<th>기대값</th>
</tr>
</thead>
<tbody>
<tr>
<td>State (상태)</td>
<td><strong>Attached</strong></td>
</tr>
<tr>
<td>VPC ID</td>
<td><code>vpc-… | task7-vpc</code></td>
</tr>
</tbody>
</table>
<blockquote>
<ul>
<li>IGW는 VPC당 <strong>1개만</strong> 연결할 수 있다. 목록에 이미 있는 다른 IGW는 기본 VPC 소속이므로 건드리지 않는다.</li>
<li>IGW를 연결만 해서는 인터넷이 되지 않는다. 다음 단계 Route Table에 <code>0.0.0.0/0 → task7-igw</code> 경로를 추가해야 서브넷이 &quot;퍼블릭&quot;이 된다.</li>
<li>정리 시에는 <strong>Detach → Delete</strong> 순서 (연결된 상태로는 삭제 불가).</li>
</ul>
</blockquote>
</details>
<p><strong>📸 증빙 캡처</strong></p>
<p><img width="100%" src="docs/screenshots/3.Internet%20gateway.png" alt="Internet Gateway - Attached" /></p>
</details>

<details>
<summary><b>4단계 · Route Table 생성 · 경로 · 서브넷 연결</b> (클릭해서 펼치기)</summary>
<p><strong>Route Table</strong> 생성: <code>task7-public-rt</code> → Routes 편집 <code>0.0.0.0/0 → task7-igw</code> → Subnet associations 에 Public Subnet 연결</p>
<blockquote>
<p>💡 <strong>개념 — RT(Route Table, 라우팅 테이블)</strong></p>
<ul>
<li>패킷이 <strong>어디로 가야 하는지</strong> 적어 둔 <strong>길 안내 표지판(내비게이션 규칙)</strong>.</li>
<li><code>10.0.0.0/16 → local</code> = &quot;단지 안 주소면 <strong>내부에서</strong> 전달&quot; (자동 생성).</li>
<li><code>0.0.0.0/0 → igw</code> = &quot;<strong>그 외 모든 주소</strong>(=인터넷)는 <strong>정문(IGW)</strong> 으로&quot; — <code>0.0.0.0/0</code> 은 &quot;모든 IP&quot;를 뜻한다.</li>
<li>이 테이블을 서브넷에 <strong>연결</strong>하는 순간 그 서브넷이 <strong>퍼블릭 서브넷</strong>이 된다. 연결 안 하면 VPC 기본 테이블(<code>local</code> 만 있음)을 따라 인터넷이 안 된다.</li>
</ul>
</blockquote>
<details>
<summary>상세 절차 (클릭)</summary>
<p><strong>(1) 라우팅 테이블 생성</strong></p>
<ol>
<li>VPC 콘솔 왼쪽 <strong>Route tables(라우팅 테이블)</strong> → <strong>Create route table(라우팅 테이블 생성)</strong></li>
<li>Name(이름): <code>task7-public-rt</code> / VPC: <strong><code>task7-vpc</code></strong></li>
<li><strong>Create route table</strong> 클릭 → 이 시점에는 <code>10.0.0.0/16 → local</code> 경로 1개만 존재</li>
</ol>
<p><strong>(2) 인터넷 경로 추가</strong></p>
<ol>
<li><strong>Routes(라우팅)</strong> 탭 → <strong>Edit routes(라우팅 편집)</strong> → <strong>Add route(라우팅 추가)</strong></li>
<li>Destination(대상): <code>0.0.0.0/0</code> / Target(대상): <strong>Internet Gateway</strong> → <code>task7-igw</code> 선택</li>
<li><strong>Save changes(변경 사항 저장)</strong></li>
</ol>
<p><strong>(3) 서브넷 연결</strong></p>
<ol>
<li><strong>Subnet associations(서브넷 연결)</strong> 탭 → <strong>명시적 서브넷 연결</strong> 의 <strong>Edit subnet associations(서브넷 연결 편집)</strong></li>
<li>☑ <code>task7-public-subnet</code> 체크 → <strong>Save associations(연결 저장)</strong></li>
</ol>
<p><strong>(4) 확인</strong></p>
<table>
<thead>
<tr>
<th>위치</th>
<th>항목</th>
<th>기대값</th>
</tr>
</thead>
<tbody>
<tr>
<td>라우팅 탭</td>
<td><code>0.0.0.0/0</code></td>
<td>→ <code>igw-…</code> (task7-igw) · 활성</td>
</tr>
<tr>
<td>라우팅 탭</td>
<td><code>10.0.0.0/16</code></td>
<td>→ <code>local</code> · 활성 (자동 생성)</td>
</tr>
<tr>
<td>서브넷 연결 탭</td>
<td>명시적 서브넷 연결</td>
<td><code>task7-public-subnet</code> (<code>10.0.1.0/24</code>)</td>
</tr>
<tr>
<td>세부 정보</td>
<td>VPC / 기본</td>
<td><code>task7-vpc</code> / 아니요</td>
</tr>
</tbody>
</table>
<blockquote>
<ul>
<li><code>0.0.0.0/0 → IGW</code> 경로가 있는 라우팅 테이블에 연결된 서브넷이 곧 <strong>퍼블릭 서브넷</strong>이다.</li>
<li>서브넷을 명시적으로 연결하지 않으면 VPC의 <strong>기본(main) 라우팅 테이블</strong>(local 경로만 있음)을 따르므로 외부 접속이 안 된다.</li>
<li>정리 시에는 <strong>서브넷 연결 해제 → 라우팅 테이블 삭제</strong> 순서.</li>
</ul>
</blockquote>
</details>
<p><strong>📸 증빙 캡처</strong></p>
<p><img width="100%" src="docs/screenshots/4.Route%20Table-1.png" alt="Route Table - 라우팅" /></p>
<p><img width="100%" src="docs/screenshots/4.Route%20Table-2.png" alt="Route Table - 서브넷 연결" /></p>
</details>

<details>
<summary><b>5단계 · Security Group 생성</b> (클릭해서 펼치기)</summary>
<p><strong>Security Group</strong> 생성 (<code>task7-vpc</code>): 인바운드 <code>HTTP 80 / 0.0.0.0/0</code>, <code>SSH 22 / My IP</code></p>
<blockquote>
<p>💡 <strong>개념 — SG(Security Group, 보안 그룹)와 포트</strong></p>
<ul>
<li>EC2 앞에 붙는 <strong>가상 방화벽 = 현관 도어락</strong>. 규칙에 <strong>허용된 것만</strong> 들어오고 나머지는 전부 차단.</li>
<li><strong>포트(Port)</strong> = 한 컴퓨터 안의 <strong>서비스별 출입문 번호</strong>. <code>80</code> = 웹(HTTP, HyperText Transfer Protocol), <code>443</code> = HTTPS(HTTP Secure, 암호화된 HTTP), <code>22</code> = 원격 접속(SSH, Secure Shell).</li>
<li><strong>인바운드</strong> = 밖 → 서버로 들어오는 요청 / <strong>아웃바운드</strong> = 서버 → 밖으로 나가는 요청.</li>
<li><strong>HTTP 80 ← <code>0.0.0.0/0</code></strong> = 웹 페이지는 <strong>누구나</strong> 볼 수 있게. <strong>SSH 22 ← 내 IP <code>/32</code></strong> = 서버 관리 문은 <strong>내 컴퓨터만</strong> (<code>/32</code> = IP 딱 1개).</li>
<li><strong>상태 저장(Stateful)</strong> = 들어온 요청에 대한 <strong>응답은 자동 허용</strong> → 응답용 아웃바운드 규칙을 따로 만들 필요 없음.</li>
</ul>
</blockquote>
<details>
<summary>상세 절차 (클릭)</summary>
<p><strong>(1) 기본 세부 정보</strong></p>
<ol>
<li>
<p>VPC 콘솔 왼쪽 <strong>보안 → Security groups(보안 그룹)</strong> → <strong>Create security group(보안 그룹 생성)</strong></p>
</li>
<li>
<p>입력</p>
<table>
<thead>
<tr>
<th>항목</th>
<th>값</th>
</tr>
</thead>
<tbody>
<tr>
<td>보안 그룹 이름</td>
<td><code>task7-web-sg</code></td>
</tr>
<tr>
<td>설명</td>
<td><code>Task7 web server SG</code> (영문만 가능)</td>
</tr>
<tr>
<td>VPC</td>
<td><strong><code>task7-vpc</code></strong> (기본 VPC가 선택되어 있으므로 반드시 변경)</td>
</tr>
</tbody>
</table>
</li>
</ol>
<p><strong>(2) 인바운드 규칙</strong> — <strong>규칙 추가</strong> 2회</p>
<table>
<thead>
<tr>
<th>유형</th>
<th>프로토콜</th>
<th>포트</th>
<th>소스</th>
<th>설명</th>
</tr>
</thead>
<tbody>
<tr>
<td>HTTP</td>
<td>TCP</td>
<td>80</td>
<td>Anywhere-IPv4 <code>0.0.0.0/0</code></td>
<td>web</td>
</tr>
<tr>
<td>SSH</td>
<td>TCP</td>
<td>22</td>
<td><strong>내 IP</strong> <code>x.x.x.x/32</code> (자동 입력)</td>
<td>my ip ssh</td>
</tr>
</tbody>
</table>
<p><strong>(3) 아웃바운드 규칙</strong> — 기본값(모든 트래픽 → <code>0.0.0.0/0</code>) 유지. 인스턴스의 <code>curl https://example.com</code> 아웃바운드 검증에 필요</p>
<p><strong>(4) Create security group</strong> 클릭</p>
<p><strong>(5) 확인</strong></p>
<table>
<thead>
<tr>
<th>항목</th>
<th>기대값</th>
</tr>
</thead>
<tbody>
<tr>
<td>보안 그룹 이름 / VPC</td>
<td><code>task7-web-sg</code> / <code>task7-vpc</code></td>
</tr>
<tr>
<td>인바운드 규칙 수</td>
<td><strong>2</strong> (HTTP 80 전체, SSH 22 내 IP <code>/32</code>)</td>
</tr>
<tr>
<td>아웃바운드 규칙 수</td>
<td>1 (전체 허용, 기본값)</td>
</tr>
<tr>
<td>전체 포트 허용 인바운드 규칙</td>
<td><strong>없음</strong></td>
</tr>
</tbody>
</table>
<blockquote>
<ul>
<li>SG는 <strong>상태 저장(stateful)</strong> — 허용된 인바운드 요청의 응답은 아웃바운드 규칙과 무관하게 나간다.</li>
<li>네트워크(집/카페 등)가 바뀌면 공인 IP가 바뀌어 SSH가 타임아웃 난다 → SSH 규칙 소스를 다시 <strong>내 IP</strong>로 수정.</li>
<li>&quot;모든 트래픽&quot;/&quot;모든 TCP&quot; 같은 전체 허용 인바운드 규칙은 과제 요구사항 위반.</li>
</ul>
</blockquote>
</details>
<p><strong>📸 증빙 캡처</strong></p>
<p><img width="100%" src="docs/screenshots/5.Security%20Group.png" alt="Security Group - 인바운드 규칙" /></p>
</details>

<details>
<summary><b>6단계 · EC2 시작</b> (클릭해서 펼치기)</summary>
<p><strong>EC2</strong> 시작: Ubuntu 24.04 LTS, <code>t3.micro</code>, 키페어 <code>task7-key</code> 생성(.pem 보관), 네트워크 <code>task7-vpc</code> / <code>task7-public-subnet</code> / 퍼블릭 IP 자동 할당 Enable / SG <code>task7-web-sg</code>, 스토리지 8GiB gp3
→ Advanced details → <strong>User data</strong> 에 <a href="scripts/setup-server.sh"><code>scripts/setup-server.sh</code></a> 내용 전체 붙여넣기</p>
<blockquote>
<p>💡 <strong>개념 — EC2와 부속 요소</strong></p>
<ul>
<li><strong>EC2(Elastic Compute Cloud)</strong> = AWS에서 빌리는 <strong>가상 컴퓨터</strong>. 필요할 때 켜고, 다 쓰면 반납(종료).</li>
<li><strong>AMI(Amazon Machine Image)</strong> = 컴퓨터에 설치할 <strong>OS 설치 이미지</strong> (여기선 Ubuntu 24.04). <strong>인스턴스 유형 <code>t3.micro</code></strong> = vCPU(virtual Central Processing Unit, 가상 CPU) 2개·메모리 1GiB짜리 <strong>사양</strong>. (<code>t</code> = 범용 버스트형 계열, <code>3</code> = 세대, <code>micro</code> = 크기)</li>
<li><strong>키 페어(.pem)</strong> = SSH 접속용 <strong>열쇠</strong>. AWS는 자물쇠(공개키)만 갖고, 열쇠(개인키 <code>.pem</code>)는 <strong>나만</strong> 가진다 → 잃어버리면 재발급 불가.</li>
<li><strong>EBS(Elastic Block Store) · gp3(General Purpose SSD 3세대) 8GiB(Gibibyte)</strong> = EC2에 꽂는 <strong>가상 하드디스크</strong>. <em>종료 시 삭제</em> 를 켜 두면 서버 반납 때 같이 사라져 요금이 안 남는다.</li>
<li><strong>User data</strong> = 서버가 <strong>처음 부팅할 때 딱 한 번 자동 실행되는 스크립트</strong> → Nginx 설치·페이지 생성을 사람이 접속하지 않아도 끝내 준다.</li>
<li><strong>IMDSv2(Instance Metadata Service version 2)</strong> = 서버가 자기 정보를 조회하는 내부 주소(메타데이터)에 <strong>토큰 인증</strong>을 강제해 해킹 위험을 줄이는 설정.</li>
</ul>
</blockquote>
<details>
<summary>상세 절차 (클릭)</summary>
<p><strong>(1) 인스턴스 시작 설정</strong> — EC2 콘솔 → <strong>인스턴스 시작</strong></p>
<table>
<thead>
<tr>
<th>항목</th>
<th>값</th>
</tr>
</thead>
<tbody>
<tr>
<td>이름</td>
<td><code>task7-web</code></td>
</tr>
<tr>
<td>AMI</td>
<td><strong>Ubuntu Server 24.04 LTS</strong> (프리 티어 사용 가능, 64비트 x86)</td>
</tr>
<tr>
<td>인스턴스 유형</td>
<td><strong>t3.micro</strong></td>
</tr>
<tr>
<td>키 페어</td>
<td><strong>새 키 페어 생성</strong> → <code>task7-key</code> / RSA / <strong>.pem</strong> → Task7 폴더에 저장 (<code>.gitignore</code> 로 커밋 제외)</td>
</tr>
<tr>
<td>네트워크 설정 → <strong>편집</strong></td>
<td>VPC <code>task7-vpc</code> / 서브넷 <code>task7-public-subnet</code> / 퍼블릭 IP 자동 할당 <strong>활성화</strong></td>
</tr>
<tr>
<td>방화벽(보안 그룹)</td>
<td><strong>기존 보안 그룹 선택</strong> → <code>task7-web-sg</code></td>
</tr>
<tr>
<td>스토리지</td>
<td>8 GiB <strong>gp3</strong> (종료 시 삭제)</td>
</tr>
<tr>
<td>고급 세부 정보 → 메타데이터 버전</td>
<td><strong>V2 전용(토큰 필수)</strong></td>
</tr>
<tr>
<td>고급 세부 정보 → <strong>사용자 데이터</strong></td>
<td><a href="scripts/setup-server.sh"><code>scripts/setup-server.sh</code></a> 내용 전체 붙여넣기</td>
</tr>
</tbody>
</table>
<p><strong>(2) 인스턴스 시작</strong> 클릭 → 2~3분 대기 (부팅 + user-data 로 Nginx 설치)</p>
<p><strong>(3) 확인</strong> — 인스턴스 요약</p>
<table>
<thead>
<tr>
<th>항목</th>
<th>기대값</th>
<th>실제</th>
</tr>
</thead>
<tbody>
<tr>
<td>인스턴스 상태</td>
<td>실행 중</td>
<td>✅ 실행 중</td>
</tr>
<tr>
<td>인스턴스 유형</td>
<td>t3.micro</td>
<td>✅</td>
</tr>
<tr>
<td>VPC / 서브넷</td>
<td><code>task7-vpc</code> / <code>task7-public-subnet</code></td>
<td>✅</td>
</tr>
<tr>
<td>퍼블릭 IPv4 / DNS</td>
<td>자동 할당 / <code>ec2-…compute.amazonaws.com</code></td>
<td>✅ (VPC DNS hostnames 활성화 결과)</td>
</tr>
<tr>
<td>프라이빗 IPv4</td>
<td><code>10.0.1.x</code></td>
<td>✅ <code>10.0.1.173</code></td>
</tr>
<tr>
<td>IMDSv2</td>
<td>Required</td>
<td>✅</td>
</tr>
<tr>
<td>키 페어</td>
<td><code>task7-key</code></td>
<td>✅</td>
</tr>
</tbody>
</table>
<blockquote>
<ul>
<li>네트워크 설정은 기본값이 <strong>기본 VPC</strong> 이므로 반드시 <strong>편집</strong>해서 <code>task7-vpc</code> 로 변경.</li>
<li><code>.pem</code> 키는 생성 시 <strong>한 번만</strong> 다운로드 가능.</li>
<li>IAM 정책상 <code>t2/t3.micro</code> 외 유형, 10GiB 초과 볼륨은 <strong>거부</strong>된다.</li>
<li>요약 화면의 <em>AWS Compute Optimizer</em> 권한 오류(<code>compute-optimizer:GetEnrollmentStatus … not authorized</code>)는 콘솔이 부가 서비스를 자동 조회하다 최소권한 정책에 막힌 것 — 실습과 무관하며 <strong>최소권한이 적용된 근거</strong>다.</li>
</ul>
</blockquote>
</details>
<p><strong>📸 증빙 캡처</strong></p>
<p><img width="100%" src="docs/screenshots/6.EC2-1.png" alt="EC2 - 인스턴스 요약" /></p>
<p><img width="100%" src="docs/screenshots/6.EC2-2.png" alt="EC2 - 인스턴스 세부 정보" /></p>
</details>

<details>
<summary><b>7단계 · 접속 확인 (/health)</b> (클릭해서 펼치기)</summary>
<p>2~3분 후 <code>http://&lt;퍼블릭IP&gt;/health</code> 확인</p>
<blockquote>
<p>💡 <strong>개념 — Nginx · HTTP 상태 코드 · 헬스 체크</strong></p>
<ul>
<li><strong>Nginx(엔진엑스, &quot;engine x&quot;)</strong> = 요청을 받아 웹 페이지를 돌려주는 <strong>웹 서버 프로그램</strong> (80번 포트에서 대기).</li>
<li><strong>HTTP(HyperText Transfer Protocol) 상태 코드</strong> = 서버의 대답 요약. <strong><code>200 OK</code></strong> = 성공, <code>404</code> = 없는 페이지, <code>5xx</code> = 서버 오류.</li>
<li><strong><code>/health</code> (헬스 체크)</strong> = &quot;서버 살아 있어?&quot; 를 확인하는 <strong>전용 주소</strong>. 항상 <code>OK</code> 한 단어만 돌려줘 자동 점검 도구가 쓰기 쉽다.</li>
<li><strong>외부 요청이 도달하는 경로</strong>: 내 PC → 인터넷 → <strong>IGW(정문)</strong> → <strong>Route Table(길 안내)</strong> → <strong>Subnet(동)</strong> → <strong>Security Group(도어락, 80 허용)</strong> → <strong>EC2 Nginx(집)</strong>. 하나라도 빠지면 타임아웃.</li>
</ul>
</blockquote>
<details>
<summary>상세 결과 (클릭)</summary>
<table>
<thead>
<tr>
<th>검증</th>
<th>결과</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>curl.exe -i http://&lt;퍼블릭IP&gt;/health</code></td>
<td><code>HTTP/1.1 200 OK</code> · <code>Server: nginx/1.24.0 (Ubuntu)</code> · <code>Content-Type: text/plain</code> · 본문 <code>OK</code></td>
</tr>
<tr>
<td>브라우저 <code>http://&lt;퍼블릭IP&gt;/</code></td>
<td>Hello Cloud 페이지 (Instance ID · AZ <code>ap-northeast-2a</code> · Private IP)</td>
</tr>
<tr>
<td>브라우저 <code>http://&lt;퍼블릭IP&gt;/health</code></td>
<td><code>OK</code></td>
</tr>
</tbody>
</table>
<p><img width="100%" src="docs/screenshots/external-health.png" alt="외부 접속 - curl" /></p>
<p><img width="100%" src="docs/screenshots/7.Hello%20Cloud.png" alt="외부 접속 - Hello Cloud" /></p>
<p><img width="100%" src="docs/screenshots/7.Health.png" alt="외부 접속 - health" /></p>
<blockquote>
<ul>
<li>반드시 <strong>http://</strong> 로 접속 (콘솔의 &quot;개방 주소법&quot; 링크는 https 로 열려 연결 실패).</li>
<li>브라우저 주소창의 &quot;주의 요함&quot;은 HTTPS가 아니어서 표시되는 것으로 정상.</li>
</ul>
</blockquote>
</details>
</details>

#### 방법 B. AWS CLI 스크립트 (Git Bash / WSL / macOS)

```bash
bash infra/provision.sh          # 내 IP 자동 조회 → 전체 생성 → /health OK 대기
# 출력된 Public IP, SSH 명령 확인
```

### 3단계. 검증

> 💡 **개념 — SSH · scp · 아웃바운드**
> - **SSH(Secure Shell)** = 원격 서버에 **암호화된 터미널**로 접속하는 방법. `ssh -i 열쇠.pem 사용자@주소` 형태 (Ubuntu AMI의 기본 사용자는 `ubuntu`).
> - **scp(Secure Copy Protocol)** = SSH 통로로 **파일을 복사**하는 명령 (내 PC → 서버).
> - **`curl`(Client URL, URL = Uniform Resource Locator)** = 터미널에서 웹 주소를 호출해 응답을 보는 도구. `curl http://localhost` = 서버가 **자기 자신**에게 요청 → Nginx 자체가 정상인지 확인.
> - **아웃바운드 확인** (`curl https://example.com`) = 서버가 **밖으로 나갈 수 있는지** (패키지 설치·업데이트에 필요).

```bash
# (1) SSH 접속 — Windows 는 먼저 키 권한 정리: docs/troubleshooting.md 사례 1 참고
ssh -i task7-key.pem ubuntu@<퍼블릭IP>

# (2) 인스턴스 내부 점검: 아웃바운드 / nginx active / localhost 200 / health OK
#     (내 PC에서 먼저 복사: scp -i task7-key.pem scripts/verify-instance.sh ubuntu@<퍼블릭IP>:~)
bash verify-instance.sh
```

```powershell
# (3) 내 PC에서 외부 접속 검증 (Windows PowerShell)
powershell -ExecutionPolicy Bypass -File scripts\verify-external.ps1 -PublicIp <퍼블릭IP>
# 또는
curl.exe -i http://<퍼블릭IP>/health
```

> Windows 키 권한 정리 — **cmd** 와 **PowerShell** 문법이 다르다 (docs/troubleshooting.md 사례 1)
>
> | 셸 | 명령 |
> |---|---|
> | cmd | `icacls task7-key.pem /inheritance:r` → `icacls task7-key.pem /grant:r "%USERNAME%:(R)"` |
> | PowerShell | `icacls task7-key.pem /inheritance:r` → `icacls task7-key.pem /grant:r "$($env:USERNAME):(R)"` |

<details>
<summary>검증 결과 (클릭)</summary>
<table>
<thead>
<tr>
<th>검증</th>
<th>결과</th>
</tr>
</thead>
<tbody>
<tr>
<td>scp 스크립트 복사</td>
<td><code>verify-instance.sh 100%</code></td>
</tr>
<tr>
<td>SSH 접속</td>
<td><code>ubuntu@ip-10-0-1-173</code> · Ubuntu 24.04.4 LTS · <code>10.0.1.173</code></td>
</tr>
<tr>
<td>아웃바운드 <code>curl https://example.com</code></td>
<td><code>HTTP/2 200</code> ✅</td>
</tr>
<tr>
<td>nginx 서비스 / 80 LISTEN</td>
<td><code>active</code> / LISTEN ✅</td>
</tr>
<tr>
<td><code>curl http://localhost</code></td>
<td>200 ✅</td>
</tr>
<tr>
<td><code>curl http://localhost/health</code></td>
<td><code>HTTP/1.1 200 OK</code> · 본문 <code>OK</code> ✅</td>
</tr>
<tr>
<td><strong>종합</strong></td>
<td><strong>PASS=6 FAIL=0</strong></td>
</tr>
</tbody>
</table>
<blockquote>
<p>SSH 로그인 시 표시되는 <code>172 updates</code> / <code>New release '26.04.1 LTS'</code> 안내는 과제와 무관하므로 업그레이드하지 않는다.</p>
</blockquote>
</details>

**📸 증빙 캡처 — SSH 접속** (`scp` 로 점검 스크립트 복사 → `ssh -i task7-key.pem ubuntu@3.36.131.116` → `ubuntu@ip-10-0-1-173` 로그인)

![SSH 접속](docs/screenshots/8.%EA%B2%80%EC%A6%9D.png)

**📸 증빙 캡처 — 인스턴스 내부 점검** (`bash verify-instance.sh` → PASS=6 FAIL=0)

![인스턴스 내부 점검](docs/screenshots/instance-verify.png)

**📸 증빙 캡처 — 외부 접속 검증** (내 PC → 인터넷 → 서버)

| 내 PC `curl.exe -i http://3.36.131.116/health` → `200 OK` / `OK` | 브라우저 `http://3.36.131.116/health` → `OK` |
|---|---|
| ![외부 접속 - curl](docs/screenshots/external-health.png) | ![외부 접속 - health](docs/screenshots/7.Health.png) |

브라우저 `http://3.36.131.116/` → Hello Cloud 페이지 (Instance ID · AZ `ap-northeast-2a` · Private IP `10.0.1.173`)

![외부 접속 - Hello Cloud](docs/screenshots/7.Hello%20Cloud.png)

### 4단계. 증빙 스크린샷 (docs/screenshots/)

| 파일명(권장) | 내용 |
|---|---|
| `external-health.png` | **(필수)** 내 PC에서 `/health` 호출 결과 (200 / OK) |
| `8.검증.png` | SSH 접속 화면 (`ubuntu@ip-10-0-1-173`) |
| `instance-verify.png` | `verify-instance.sh` PASS 결과 (아웃바운드, localhost 200) |
| `5.Security Group.png` | 보안 그룹 인바운드 규칙 (80 전체, 22 내 IP) |
| `1.VPC.png` | VPC `task7-vpc` 세부 정보 (CIDR `10.0.0.0/16`, DNS 호스트 이름 활성화됨) |
| `2.Subnet.png` | Subnet `task7-public-subnet` 세부 정보 (`ap-northeast-2a`, 퍼블릭 IPv4 자동 할당: 예, RT `task7-public-rt`) |
| `3.Internet gateway.png` | IGW `task7-igw` Attached → `task7-vpc` |
| `4.Route Table-1.png`, `4.Route Table-2.png` | Route Table `0.0.0.0/0 → igw` (라우팅) + 서브넷 연결 |
| `6.EC2-1.png`, `6.EC2-2.png` | EC2 `task7-web` 인스턴스 요약 / 세부 정보 |
| `7.Hello Cloud.png`, `7.Health.png` | 브라우저 `/`, `/health` 접속 결과 |
| `iam-policy_1.png`, `iam-policy_2.png` | `task7-user` 권한 (Task7LeastPrivilege 만 연결) |
| `cleanup-ec2-confirm.png`, `cleanup-ec2.png` | EC2 종료(삭제) 확인 창 / 인스턴스 상태 **종료됨** |
| `cleanup-volume.png`, `cleanup-탄력적ip.png` | EBS 볼륨 / 탄력적 IP 목록 비어 있음 |
| `cleanup-keypair.png` | 키 페어 `task7-key` 삭제 완료 |
| `cleanup-sg.png` | 보안 그룹 `task7-web-sg` 삭제 완료 |
| `B1-cleanup-rt.png`, `B2-cleanup-rt.png`, `cleanup-rt.png` | 라우팅 테이블 서브넷 연결 해제 / 삭제 확인 / 삭제 완료 |
| `B1-cleanup-igw.png`, `B2-cleanup-igw.png`, `cleanup-igw.png` | IGW 분리 / 삭제 확인 / 삭제 완료 |
| `B1-cleanup-subnet.png`, `cleanup-subnet.png` | 서브넷 삭제 확인 / 삭제 완료 |
| `B1-cleanup-vpc.png`, `B2-cleanup-vpc.png`, `cleanup-vpc.png` | VPC 선택 / 삭제 확인 / 삭제 완료 |
| `cleanup-billing.png` | Billing 화면 (루트 계정) |

### 5단계. 리소스 정리 (필수)

> 💡 **개념 — 왜 정리하고, 왜 이 순서인가?**
> - 클라우드는 **켜져 있는 시간만큼 과금**된다. 실행 중 EC2(Elastic Compute Cloud), EBS(Elastic Block Store) 디스크, 퍼블릭 IPv4(Internet Protocol version 4) 가 대표적. **중지(Stop)** 는 디스크 요금이 계속 나가므로 **종료(Terminate)** 해야 한다.
> - 리소스끼리 **서로 붙잡고 있어서**(의존 관계) 붙잡는 쪽부터 지워야 삭제된다:
>   **EC2**(SG·서브넷 사용) → **SG** → **Route Table**(서브넷 연결) → **IGW**(VPC에 부착, 먼저 *분리*) → **Subnet** → **VPC**
> - 기본 VPC(`172.31.0.0/16`)와 그 부속(default SG, main RT, IGW, 서브넷 4개)은 AWS가 계정마다 **기본 제공**하는 것 — 과금 없음, 정리 대상 아님.

```bash
bash infra/cleanup.sh            # CLI로 만든 경우 — 역순 삭제 + 잔존 리소스 0개 검증
```

콘솔로 만들었다면 [`docs/cleanup-checklist.md`](docs/cleanup-checklist.md) 순서대로 삭제하고 근거를 남긴다.

**EC2 종료 (Terminate)**

![EC2 종료(삭제) 확인 창](docs/screenshots/cleanup-ec2-confirm.png)

![EC2 종료됨](docs/screenshots/cleanup-ec2.png)

**EBS 볼륨 · 탄력적 IP 잔존 확인** — 둘 다 목록 비어 있음 (루트 볼륨은 종료 시 자동 삭제, EIP는 할당하지 않음)

![EBS 볼륨 없음](docs/screenshots/cleanup-volume.png)

![탄력적 IP 없음](docs/screenshots/cleanup-%ED%83%84%EB%A0%A5%EC%A0%81ip.png)

**키 페어 삭제** — `task7-key` 삭제 완료 (로컬 `task7-key.pem` 도 더 이상 사용 불가)

![키 페어 삭제](docs/screenshots/cleanup-keypair.png)

**보안 그룹 삭제** — `task7-web-sg` 삭제 완료, 각 VPC의 `default` SG만 남음 (default SG는 VPC 삭제 시 함께 삭제)

![보안 그룹 삭제](docs/screenshots/cleanup-sg.png)

**라우팅 테이블 삭제** — 서브넷 연결 해제 → 삭제 확인(`삭제` 입력) → `task7-public-rt` 삭제 완료. 남은 2개는 각 VPC의 **기본(main)** 라우팅 테이블 (task7-vpc 것은 VPC 삭제 시 함께 삭제)

![라우팅 테이블 - 서브넷 연결 해제](docs/screenshots/B1-cleanup-rt.png)

![라우팅 테이블 - 삭제 확인](docs/screenshots/B2-cleanup-rt.png)

![라우팅 테이블 - 삭제 완료](docs/screenshots/cleanup-rt.png)

**인터넷 게이트웨이 분리 → 삭제** — `task7-igw`(`igw-0e2a1faedc86eb077`) 삭제 완료. 남은 1개는 **기본 VPC**(`vpc-083cf4b2…`)의 IGW로 원래 존재하던 것

![IGW - 분리](docs/screenshots/B1-cleanup-igw.png)

![IGW - 삭제 확인](docs/screenshots/B2-cleanup-igw.png)

![IGW - 삭제 완료](docs/screenshots/cleanup-igw.png)

**서브넷 삭제** — `task7-public-subnet`(`subnet-023ecedbf31fd455e`) 삭제 완료. 남은 4개(`172.31.x.x/20`)는 **기본 VPC** 서브넷

![Subnet - 삭제 확인](docs/screenshots/B1-cleanup-subnet.png)

![Subnet - 삭제 완료](docs/screenshots/cleanup-subnet.png)

**VPC 삭제** — `task7-vpc`(`vpc-0e9f70c7c82a8fc67`) 삭제 완료 (task7-vpc의 기본 RT · 기본 SG · 기본 NACL 도 함께 삭제). 남은 1개는 **기본 VPC** `172.31.0.0/16`

![VPC - 대상 선택](docs/screenshots/B1-cleanup-vpc.png)

![VPC - 삭제 확인](docs/screenshots/B2-cleanup-vpc.png)

![VPC - 삭제 완료](docs/screenshots/cleanup-vpc.png)


**Billing 확인 (루트 계정)** — 2026년 9월 청구서 예상 총합계 **USD 0.00** (무료 플랜 계정, 요금 청구 없음)

![Billing - 청구서](docs/screenshots/cleanup-billing.png)

> ✅ **정리 완료 (2026-09-30)** — task7 리소스(EC2 · EBS · Key Pair · SG · RT · IGW · Subnet · VPC) 잔존 0개. 상세 근거: [`docs/cleanup-checklist.md`](docs/cleanup-checklist.md)

| 항목 | 내용 |
|---|---|
| 대상 | `i-0ef580f56d69a62a6 (task7-web)` · 종료 방지: 비활성 |
| 옵션 | *OS 종료 건너뛰기* **미체크** (정상 종료) |
| 효과 | 루트 EBS 볼륨 함께 삭제(종료 시 삭제 설정) → EBS 과금 없음 |
| 결과 | **종료됨(Terminated)** · 퍼블릭 IPv4/DNS 반납(`–`) |

> 종료(Terminate)는 되돌릴 수 없고 퍼블릭 IP `3.36.131.116` 도 반납된다. 중지(Stop)는 EBS 요금이 계속 발생하고 재시작 시 IP가 바뀌므로 사용하지 않는다.

---

## 요구사항 충족 매핑

| 요구사항 | 구현 / 근거 |
|---|---|
| VPC 1 / Public Subnet 1 / IGW 연결 | 2단계, `infra/provision.sh` 1~3 |
| `0.0.0.0/0 → IGW` 경로 | Route Table `task7-public-rt` (screenshot `4.Route Table-1.png`, `4.Route Table-2.png`) |
| 인스턴스 아웃바운드 (`curl https://example.com`) | `verify-instance.sh` 첫 항목 |
| EC2 1대 + SSH 접속 | 3단계 (1) |
| Nginx 설치·실행 / `curl http://localhost` 200 | `setup-server.sh`, `verify-instance.sh` |
| SG: 80 전체, 22 내 IP, 전체 포트 허용 없음 | `task7-web-sg` (screenshot `5.Security Group.png`) |
| IAM 사용자 1개, EC2/VPC/SG 범위, Admin 없음 | `iam/task7-least-privilege-policy.json` |
| 외부 접속 검증 (B) | 상단 "외부 접속 검증" 표 + `external-health.png` |
| 리소스 정리 (EC2, EBS, EIP, IGW, VPC) | `infra/cleanup.sh`, `docs/cleanup-checklist.md` |

---

## 개념 정리 (과제 목표)

**트래픽 흐름** — 인터넷 요청은 `IGW`(VPC의 인터넷 출입문) → `Route Table`(`0.0.0.0/0 → IGW` 경로가 있어야 "퍼블릭" 서브넷) → `Public Subnet` → `Security Group`(인스턴스 단위 방화벽, 80 허용) → `EC2 Nginx` 순으로 도달한다. 응답은 SG가 **상태 저장(stateful)** 이므로 별도 아웃바운드 규칙 없이 돌아간다.

**외부 접속에 필요한 3가지** — ① 퍼블릭 IP(또는 EIP) ② IGW로 가는 라우팅 ③ SG 인바운드 허용. 하나라도 빠지면 타임아웃이 난다.

**Security Group vs IAM** — SG는 *네트워크 패킷*이 인스턴스에 들어올 수 있는지(누가 어느 포트로), IAM은 *AWS API 호출*을 누가 할 수 있는지(누가 무엇을 만들고 지울지)를 통제한다. 둘 다 "필요한 것만 허용"하는 최소권한 원칙을 적용한다 — SG는 22번을 내 IP로 제한, IAM은 서비스·리전·인스턴스 타입을 제한.

**과금 요인과 정리 순서** — 실행 중 EC2, EBS 볼륨(중지 상태에도 과금), 할당된 Elastic IP/퍼블릭 IPv4, NAT Gateway·ALB·RDS가 대표적이다. 리소스 간 참조 관계 때문에 EC2 → EIP → SG → RT → IGW → Subnet → VPC 순서로 지운다.
