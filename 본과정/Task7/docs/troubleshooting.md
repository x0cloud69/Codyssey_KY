# 트러블슈팅 보고서

> 작성 규칙: 각 건마다 **증상 → 가설 → 검증 → 조치 → 결과 → 재발방지** 순서로, 근거(로그·명령 출력·스크린샷)를 함께 남긴다.
>
> 아래 2건은 이 실습(2026-09-30, `ap-northeast-2`, 사용자 `task7-user`)에서 **실제로 발생한 사례**다.

---

## 0. 외부 접속 불가 시 점검 순서 (바깥 → 안쪽)

외부 요청은 아래 순서로 통과해야 EC2 웹 서버에 도달한다. 한 단계씩 확인하면 원인을 빠르게 좁힐 수 있다.

| 단계 | 확인 대상 | 확인 방법 | 정상 기준 |
|---|---|---|---|
| 1 | 퍼블릭 IP | EC2 콘솔 → 인스턴스 상세 | Public IPv4 주소 존재 |
| 2 | IGW 연결 | VPC 콘솔 → Internet Gateways | State = `Attached` (task7-vpc) |
| 3 | 라우팅 | Route Tables → Routes / Subnet associations | `0.0.0.0/0 → igw-…` + Public Subnet 연결 |
| 4 | 보안 그룹 | SG → Inbound rules | `80 ← 0.0.0.0/0`, `22 ← 내 IP/32` |
| 5 | 웹 서버 | (SSH) `systemctl status nginx`, `ss -ltn` | `active (running)`, `:80 LISTEN` |
| 6 | 로컬 응답 | (SSH) `curl -i http://localhost/health` | `200 OK` / `OK` |
| 7 | 서버 로그 | `/var/log/nginx/error.log`, `/var/log/setup-server.log` | 에러 없음 |

> 팁: **타임아웃**(응답 없음)은 보통 네트워크 계층(IGW·라우팅·SG) 문제, **Connection refused / 4xx / 5xx** 는 서버(Nginx) 문제다.

---

## 사례 1. Windows에서 `.pem` 권한 정리 중 셸 문법 차이로 키를 읽지 못함 (실제 발생)

| 항목 | 내용 |
|---|---|
| **증상** | `scp -i task7-key.pem …` 실행 시 `Load key "task7-key.pem": Permission denied` → `ubuntu@3.36.131.116: Permission denied (publickey).` / `scp: Connection closed` |
| **배경** | Windows OpenSSH는 키 파일에 본인 외 사용자 권한이 있으면 사용을 거부하므로, 먼저 `icacls` 로 권한을 정리하려 했다 |
| **원인 가설** | ① 키 파일 권한이 **너무 넓음**(Users 그룹 읽기) → 보통 `UNPROTECTED PRIVATE KEY FILE` 경고가 뜸<br>② 권한이 **아예 없음** → `Load key … Permission denied` 가 뜸 → 이번 증상은 ② |
| **검증** | 실행 기록 확인:<br>`icacls task7-key.pem /inheritance:r` → **성공** (상속 권한 전부 제거)<br>`icacls task7-key.pem /grant:r "$($env:USERNAME):(R)"` → `매개 변수가 잘못되었습니다` **실패**<br>→ `$($env:USERNAME)` 은 **PowerShell 문법**인데 **cmd** 에서 실행 → 본인 읽기 권한이 부여되지 않아 **아무도 읽을 수 없는 파일**이 됨 |
| **조치** | cmd 문법으로 재실행: `icacls task7-key.pem /grant:r "%USERNAME%:(R)"` → `1 파일을 처리했으며` |
| **결과** | `scp` 100% 전송, `ssh -i task7-key.pem ubuntu@3.36.131.116` 접속 성공 → `verify-instance.sh` PASS=6 (스크린샷: `screenshots/8.검증.png`, `screenshots/instance-verify.png`) |
| **재발 방지** | README에 **cmd / PowerShell 명령을 구분**해 표기 / 명령 실행 전 프롬프트(`C:\>` = cmd, `PS C:\>` = PowerShell) 확인 / 키 파일은 `.gitignore`(`*.pem`)로 커밋 차단 |

---

## 사례 2. EC2 콘솔에 Compute Optimizer 권한 거부 오류 표시 (실제 발생)

| 항목 | 내용 |
|---|---|
| **증상** | EC2 인스턴스 `task7-web` 요약 화면의 **AWS Compute Optimizer 찾기** 칸에 빨간 오류:<br>`User: arn:aws:iam::<계정ID>:user/task7-user is not authorized to perform: compute-optimizer:GetEnrollmentStatus on resource: * because no identity-based policy allows the compute-optimizer:GetEnrollmentStatus action` |
| **원인 가설** | ① 인스턴스·네트워크 설정 오류로 서비스가 비정상 동작<br>② EC2 콘솔이 화면 표시를 위해 **부가 서비스(Compute Optimizer) API를 자동 호출**했는데, `task7-user` 정책에 해당 권한이 없어 거부됨 |
| **검증** | ① 인스턴스 상태 `실행 중`, 외부 `curl -i http://3.36.131.116/health` → `200 OK`/`OK`, 내부 `verify-instance.sh` PASS=6 → **서비스는 정상** → 가설 ① 기각<br>② 오류 문구가 `no identity-based policy allows` → 명시적 Deny가 아닌 **허용 누락(암묵적 거부)**<br>③ `iam/task7-least-privilege-policy.json` 에 `compute-optimizer:*` 액션 **없음** 확인 → 가설 ② 채택 |
| **조치** | **정책을 변경하지 않음.** Compute Optimizer(인스턴스 크기 추천)는 과제 요구 범위(EC2/VPC/SG) 밖이므로 권한을 추가하지 않는 것이 최소권한 원칙에 맞다 |
| **결과** | 오류 표시는 남지만 실습 기능에 영향 없음. 오히려 `task7-user` 가 **허용된 서비스 외에는 호출할 수 없음**을 보여주는 증거 (스크린샷: `screenshots/6.EC2-1.png`) |
| **재발 방지 / 교훈** | 콘솔의 권한 오류는 곧바로 권한을 넓히지 말고 **① 과제 기능에 영향이 있는지 ② 어떤 액션이 거부됐는지 ③ 그 액션이 정말 필요한지** 순서로 판단 / `explicit deny`(정책의 Deny 문) 와 `no identity-based policy allows`(허용 누락) 를 구분해 원인 파악 |

---

## 부록. 로그 확인 명령 모음

```bash
# 웹 서버
sudo systemctl status nginx --no-pager
sudo ss -ltnp | grep ':80'
sudo tail -n 50 /var/log/nginx/error.log
sudo tail -n 20 /var/log/nginx/access.log      # 외부 요청이 서버까지 왔는지 확인

# 초기 설정(user-data) 실행 로그
sudo tail -n 50 /var/log/setup-server.log
sudo tail -n 50 /var/log/cloud-init-output.log

# 인스턴스 요구사항 자체 점검
bash verify-instance.sh
```

```powershell
# 내 PC(Windows)
curl.exe -i http://<퍼블릭IP>/health
Test-NetConnection <퍼블릭IP> -Port 80
Test-NetConnection <퍼블릭IP> -Port 22
```
