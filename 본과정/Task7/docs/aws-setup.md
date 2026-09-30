# AWS 환경 구축 가이드 (0단계)

> AWS 계정이 없는 상태에서 **IAM 사용자(`task7-user`)로 서울 리전 콘솔에 로그인**하기까지의 준비 과정.
> 이 문서를 끝낸 뒤 [`README.md`](../README.md)의 2단계(인프라 생성)로 넘어간다.
>
> ※ AWS 콘솔 메뉴 이름·위치는 업데이트로 조금씩 달라질 수 있다. 막히면 콘솔 상단 검색창에 서비스 이름(IAM, Budgets 등)을 입력하면 된다.

---

## 전체 흐름

```text
[A] 계정 가입 ─→ [B] 루트 보안(MFA) ─→ [C] 과금 알림 설정 ─→ [D] IAM 정책/사용자 생성
     (루트)            (루트)                 (루트)                    (루트)
                                                                           │
          ┌────────────────────────────────────────────────────────────────┘
          ▼
[E] task7-user 로 로그인 + 서울 리전 선택 ─→ [F] 내 PC 도구 준비 ─→ README 2단계
          (여기부터 루트 사용 금지)
```

> **루트 계정은 A~D (초기 설정) 에만 사용**하고, 이후 실습은 전부 `task7-user` 로 한다. (제약사항 7)

---

## A. AWS 계정 가입

| 준비물 | 비고 |
|---|---|
| 이메일 주소 | 루트 계정 로그인 ID가 된다 |
| 신용카드 또는 해외결제 가능한 체크카드 | 본인 확인용. 소액 승인 후 취소될 수 있음 |
| 휴대폰 | 문자/음성 인증 |

1. https://aws.amazon.com → **AWS 계정 생성** (Create an AWS Account)
2. 루트 사용자 이메일, 계정 이름(예: `ky-codyssey`) 입력 → 이메일 인증 코드 입력 → 루트 비밀번호 설정
3. 연락처 정보: **개인(Personal)** 선택, 영문 주소 입력
4. 결제 정보(카드) 입력 → 휴대폰 인증
5. 플랜 선택: **Free plan (무료 플랜)** 선택
   - 신규 계정은 크레딧이 제공되며, 무료 플랜은 직접 유료로 전환하기 전까지 요금이 청구되지 않는다.
6. 가입 완료 후 계정 활성화 메일을 받을 때까지 대기 (보통 수 분)

---

## B. 루트 계정 보안 설정 (MFA)

> 루트 계정은 모든 권한을 가진 계정이라 탈취되면 치명적이다. 가입 직후 MFA부터 켠다.

1. 루트 이메일로 콘솔 로그인 → 우측 상단 계정 이름 → **보안 자격 증명(Security credentials)**
2. **MFA 디바이스 할당** → *인증 관리자 앱* 선택
3. 휴대폰의 Google Authenticator / Microsoft Authenticator 등으로 QR 스캔 → 연속된 코드 2개 입력
4. 같은 화면에서 **루트 액세스 키가 없는지** 확인 (있다면 삭제, 절대 만들지 않음)

---

## C. 과금 알림 설정 (Zero spend budget)

> 실수로 리소스를 남겨도 **1센트라도 과금되면 메일이 오도록** 안전장치를 건다.

1. 콘솔 검색창 → **Budgets** (Billing and Cost Management → 예산)
2. **예산 생성** → *템플릿 사용(Use a template)* → **Zero spend budget (제로 지출 예산)**
3. 알림 받을 이메일 입력 → 생성
4. (선택) Billing → **Free Tier** 페이지에서 무료 사용량/크레딧 잔액 확인 가능

---

## D. IAM 정책 · 사용자 생성 (최소권한)

### D-1. 정책 만들기

1. 콘솔 검색창 → **IAM** → 왼쪽 **정책(Policies)** → **정책 생성**
2. 정책 편집기에서 **JSON** 탭 선택
3. 기존 내용을 지우고 [`iam/task7-least-privilege-policy.json`](../iam/task7-least-privilege-policy.json) 내용 전체 붙여넣기
4. 다음 → 정책 이름 `Task7LeastPrivilege` → **정책 생성**

### D-2. 사용자 만들기

1. IAM → **사용자(Users)** → **사용자 생성**
2. 사용자 이름 `task7-user`
3. ☑ **AWS Management Console에 대한 사용자 액세스 권한 제공**
   - *IAM 사용자를 생성하고 싶음* 선택
   - 콘솔 암호: 사용자 지정 암호 입력
   - ☐ **"다음 로그인 시 새 암호를 생성해야 합니다" 체크 해제**
     (체크하면 암호 변경용 정책 `IAMUserChangePassword` 가 자동으로 추가되어 정책이 2개가 됨)
4. 권한 설정: **직접 정책 연결(Attach policies directly)** → `Task7LeastPrivilege` **하나만** 체크
   - ❌ `AdministratorAccess` 등 다른 정책은 체크하지 않는다
5. 검토 → **사용자 생성** → 로그인 정보 `.csv` 다운로드 (안전한 곳에 보관)
6. 증빙: 사용자 → `task7-user` → **권한** 탭 캡처 → `docs/screenshots/iam-policy_1.png`, `iam-policy_2.png`

### D-3. IAM 로그인 URL 확인

- IAM → **대시보드** 오른쪽 *AWS 계정* → **로그인 URL** 복사
  형식: `https://<12자리 계정ID>.signin.aws.amazon.com/console`
- (선택) 계정 별칭을 만들면 `https://<별칭>.signin.aws.amazon.com/console` 로 쓸 수 있음

### D-4. (CLI 방식을 쓸 때만) 액세스 키 발급

> 콘솔로만 실습(README 방법 A)하면 **건너뛴다.** 키는 유출 시 위험하므로 필요할 때만 만든다.

1. IAM → 사용자 → `task7-user` → **보안 자격 증명** → **액세스 키 만들기** → *CLI* 선택
2. 액세스 키 ID / 비밀 액세스 키 `.csv` 다운로드 (비밀 키는 이 화면에서만 볼 수 있음)
3. 실습 종료 후 **액세스 키 비활성화/삭제** (정리 체크리스트 대상)

---

## E. task7-user 로 로그인 + 리전 선택

1. **루트에서 로그아웃**
2. D-3의 IAM 로그인 URL 접속 → 사용자 이름 `task7-user` / 암호 입력
3. 콘솔 우측 상단 리전 선택 → **아시아 태평양(서울) ap-northeast-2**
   - 리전이 다르면 만든 리소스가 안 보이거나, 정책 조건 때문에 **권한 오류**가 난다
4. 확인: 우측 상단 계정 표시가 `task7-user @ <계정ID>` 형태인지 확인

> ⚠️ `task7-user` 는 EC2/VPC 외 서비스 권한이 없으므로 S3·IAM·Billing 화면 등에서 "권한 없음"이 뜨는 것이 **정상**이다. (최소권한이 잘 적용됐다는 증거)

---

## F. 내 PC(Windows) 도구 준비

| 도구 | 필요 여부 | 확인 / 설치 |
|---|---|---|
| **SSH 클라이언트** | 필수 | PowerShell에서 `ssh -V` → 버전이 나오면 OK (Windows 10/11 기본 포함) |
| 브라우저 | 필수 | 콘솔 작업, `http://<퍼블릭IP>` 확인 |
| `curl.exe` | 권장 | PowerShell에서 `curl.exe --version` (Windows 기본 포함) |
| AWS CLI v2 | 방법 B만 | PowerShell(관리자): `msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi` → 새 터미널에서 `aws --version` |
| Git Bash | 방법 B만 | `infra/*.sh` 실행용 (Git for Windows에 포함) |

**AWS CLI 설정 (방법 B만)**

```powershell
aws configure --profile task7
# AWS Access Key ID     : (D-4에서 받은 키)
# AWS Secret Access Key : (D-4에서 받은 비밀 키)
# Default region name   : ap-northeast-2
# Default output format : json

aws sts get-caller-identity --profile task7   # Arn 이 ...:user/task7-user 이면 성공
```

---

## 준비 완료 체크

- [ ] AWS 계정 가입 완료 (Free plan)
- [ ] 루트 계정 MFA 설정, 루트 액세스 키 없음
- [ ] Zero spend budget 알림 생성
- [ ] `Task7LeastPrivilege` 정책 생성
- [ ] `task7-user` 생성 — 연결된 정책은 `Task7LeastPrivilege` 1개뿐
- [ ] `task7-user` 로 콘솔 로그인, 리전 = 서울(ap-northeast-2)
- [ ] `ssh -V` 동작 확인
- [ ] (방법 B만) `aws sts get-caller-identity --profile task7` 성공

→ 모두 완료했으면 [`README.md`](../README.md) **2단계. 인프라 생성**으로 이동

---

## 참고: 실습 종료 후 Billing 확인은?

`task7-user` 는 최소권한 원칙상 Billing 권한이 없다. 정리 후 Billing Dashboard / Free Tier 확인은 **계정 관리 목적으로 루트(MFA)로 잠깐 로그인해 조회만** 하고 바로 로그아웃한다. (조회 외 작업은 하지 않음)
