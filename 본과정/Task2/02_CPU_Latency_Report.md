# [Bug] CPU Latency — agent-leak-app, CPU 사용률 점진 상승으로 임계 초과 후 Watchdog 보호 종료

> **요약**: `agent-leak-app`의 `CpuWorker`가 CPU 사용률을 점진적으로 끌어올리다가 임계치를 넘어선 52.79% 시점에서 과점유 방지 정책(`Watchdog`)에 의해 보호 종료되었다. CPU 시나리오는 `MEMORY_LIMIT`을 512MB로 올려 메모리 경고를 해소한 상태에서 트리거된다.

| 항목 | 값 |
|---|---|
| 장애 유형 | CPU Latency (CPU 과점유 → Watchdog 보호 종료) |
| 대상 프로세스 | `agent-leak-app` (`CpuWorker`) |
| 실행 계정 | `agentuser` (uid=1001) |
| 발생 시각 | 2026-06-16 10:39:28 (부팅) ~ 10:39:56 (임계 위반) |
| 환경 | MEMORY_LIMIT=512MB(OK), CPU_MAX_OCCUPY=80%, MULTI_THREAD_ENABLE=True |
| 임계 위반 지점 | CPU Load 52.79% |

---

## 1. Description (현상 설명)

- **무엇이**: 부팅 직후 `CpuWorker`가 동작하며 프로세스의 CPU 사용률을 단계적으로 끌어올렸고, 임계치를 초과하자 `[CRITICAL] CPU Threshold Violated!`가 기록되며 종료 절차로 진입했다.
- **언제**: 2026-06-16 10:39:28 부팅 → **10:39:56에 CPU 임계 위반**. 약 26초간 부하 상승.
- **어떤 조건에서**: `MEMORY_LIMIT=512MB`(메모리 정상 처리), `CPU_MAX_OCCUPY=80%`, CPU 항목에 `[ WARNING: Recommend Under 50% ]` 경고가 있는 상태.
- **재현 경로 (중요)**: 기본 상태(MEMORY_LIMIT=256)에서는 메모리 경고로 인해 `MemoryWorker`(OOM)가 동작한다. **`MEMORY_LIMIT`을 512MB로 올려 메모리 경고를 OK로 해소하면**, 앱이 다음으로 경고 상태인 **CPU 자원을 대상으로 `CpuWorker` 부하 테스트를 수행**한다. 즉 이 앱은 WARNING 상태인 자원을 골라 부하를 가하는 구조다.
- **관측된 패턴**: CPU Load가 5.00% → 52.79%로 **점진 상승**(중간에 38%대 정체 구간 포함)하다가, 52.79%에서 임계 위반 처리되었다.

---

## 2. Evidence & Logs (증거 자료)

### 2-1. 애플리케이션 실행 로그 — CPU Load 추이

`CpuWorker`가 보고한 CPU 부하. OOM의 메모리(일정한 선형 증가)와 달리, **점진적으로 상승**하며 중간 정체 구간이 있다.

| 시각 | 경과(초) | CPU Load |
|---|---:|---:|
| 10:39:30 | 0 | 5.00% |
| 10:39:33 | 3 | 14.47% |
| 10:39:38 | 8 | 23.42% |
| 10:39:41 | 11 | 29.43% |
| 10:39:44 | 14 | 35.60% |
| 10:39:47 | 17 | 38.49% |
| 10:39:50 | 20 | 38.97% |
| 10:39:53 | 23 | 45.82% |
| 10:39:56 | 26 | **52.79% → 임계 위반** |

### 2-2. 부팅 자원 점검 및 임계 위반 로그 발췌

자원 점검 단계 — 메모리는 OK, CPU만 경고:

```text
==================================================
 [ Agent Initiate ] Resource Check
==================================================
 [ MEMORY ] Limit: 512MB   [ OK ]
 [ CPU    ] Limit: 80%      [ WARNING: Recommend Under 50% ]
 [ THREAD ] Concurrency: True [ WARNING ]
```

CpuWorker 동작 및 임계 위반:

```text
2026-06-16 10:39:30,396 [INFO] [CpuWorker] Started. Maximum CPU Limit: 80%
2026-06-16 10:39:30,397 [INFO] [CpuWorker] Current Load: 5.00%
...
2026-06-16 10:39:56,680 [INFO] [CpuWorker] Current Load: 52.79%
2026-06-16 10:39:56,784 [CRITICAL] [CpuWorker] CPU Threshold Violated! (52.79%)
```

### 2-3. 종료(Watchdog / SIGTERM) 로그

> ⚠️ **직접 채워야 하는 부분.** 현재 캡처는 `CPU Threshold Violated!` 직후에서 끊겼다. 미션 요건상 **과점유 방지 정책(Watchdog)이 SIGTERM으로 종료시키는 로그**가 필요하다. 동일 명령으로 재실행하여 위반 이후 라인까지 전체 로그를 확보할 것.

```bash
# 메모리 경고를 OK로 만들어 CPU 시나리오 트리거 → 전체 로그 저장
docker run --name agent-cpu -e MEMORY_LIMIT=512 -p 15034:15034 agent-leak-app:latest
docker logs agent-cpu > app_cpu.log         # 위반 이후 WATCHDOG/SIGTERM 라인 포함 확보
```

*(예상 로그 형태: `[Watchdog] CPU overuse ... sending SIGTERM` 등 — 실제 캡처로 교체)*

### 2-4. 시스템 도구(top / monitor.sh)의 CPU 수치

> ⚠️ **직접 채워야 하는 부분.** `ps`의 `%cpu`는 생애 평균이라 순간 스파이크를 놓치므로, **순간 CPU는 `top`으로** 잡는 것이 정확하다. CpuWorker가 도는 동안 아래로 캡처.

```bash
# 컨테이너 안에서, CpuWorker 동작 중 순간 CPU 스냅샷
top -b -n 1 | head -15
# 또는 monitor.sh의 cpu_percent 컬럼 사용
```

| 측정 시각 | %CPU (top) | 비고 |
|---|---:|---|
| (입력) | (입력) | |
| (입력) | (입력) | |

*(top 출력 스크린샷 또는 monitor.log 첨부)*

---

## 3. Root Cause Analysis (원인 분석)

### 3-1. 직접 원인 — CPU 과점유 (특정 프로세스 단독)

시스템 전체 부하가 아니라 **`agent-leak-app` 단일 프로세스의 CPU 사용률이 단계적으로 상승**했다. `CpuWorker`가 연산 부하를 계속 가하여 사용률이 5% → 52.79%까지 올랐다. 시스템 전체가 아닌 특정 프로세스의 점유율이 오르는 것은 `top -H`나 `ps`로 해당 PID의 `%CPU`만 높은 것을 통해 확인할 수 있다.

### 3-2. 종료 메커니즘 — 오류가 아닌 보호 정책(Watchdog)

이 종료는 **버그로 인한 비정상 크래시가 아니라, 과점유 방지 정책(Watchdog)에 의한 의도된 보호 조치**다. CPU 임계치를 초과하자 Watchdog가 개입하여 프로세스를 정리했다(미션 요건상 SIGTERM으로 예상). OOM 사례의 `MemoryGuard`와 짝을 이루는, 애플리케이션 레벨의 자체 보호 장치다.

| 구분 | 이번 사례 (보호 정책) | 비정상 크래시 |
|---|---|---|
| 종료 트리거 | CPU 임계 초과 감지 → Watchdog | 예외/세그폴트 등 비정상 |
| 성격 | 시스템 안정성 보호를 위한 **정상 동작** | 의도치 않은 오류 |
| 증거 | `CPU Threshold Violated!` + Watchdog 종료 로그 | 스택 트레이스, 비정상 종료 코드 |
| 신호 | SIGTERM (정중한 종료 요청, 예상) | 다양 |

### 3-3. 관련 OS 동작 원리

한 프로세스가 CPU를 과도하게 점유하면, 운영체제의 스케줄러가 다른 프로세스에 CPU 시간을 충분히 배분하지 못해 **시스템 전체가 느려지는 지연(latency)**이 발생한다. 따라서 Watchdog는 특정 프로세스가 임계치를 넘기면 미리 차단하여 시스템 전체의 응답성을 보호한다.

### 3-4. 관찰 — 위반 임계가 80%가 아닌 ~50%로 보임

표시된 `Maximum CPU Limit`은 80%였으나, 실제 위반은 **52.79%**(권장선 "Under 50%"를 막 넘긴 지점)에서 발생했다. 즉 위반 판정 기준이 설정값 80%가 아니라 **권장 한계 50% 근처**일 가능성이 있다. `CPU_MAX_OCCUPY` 값을 바꿔(예: 50 vs 90) 재실행하면 실제 기준을 검증할 수 있다.

---

## 4. Workaround & Verification (조치 및 검증)

### 4-1. 임시 조치 — CPU_MAX_OCCUPY 조정

```bash
# 예시: CPU 임계 상향 후 재실행
docker run --name agent-cpu -e MEMORY_LIMIT=512 -e CPU_MAX_OCCUPY=90 -p 15034:15034 agent-leak-app:latest
```

> 주의: CPU 항목이 OK 상태가 될 만큼 조정하면, 앱이 CPU 테스트를 건너뛰고 다음 경고 자원(THREAD → Deadlock)으로 넘어갈 수 있다. CPU 시나리오를 유지하려면 CPU가 테스트 대상으로 남는 값으로 실험할 것.

### 4-2. Before & After 비교

> ⚠️ **직접 채워야 하는 부분.** `CPU_MAX_OCCUPY` 변경 전후로 **종료 여부 또는 위반까지 걸린 시간/부하**가 어떻게 달라지는지 기록.

| 구분 | CPU_MAX_OCCUPY | 위반 지점(CPU Load) | 위반까지 시간 | 종료 여부 |
|---|---:|---:|---:|---|
| Before | 80% | 52.79% | 약 26초 | 위반 → 종료 |
| After | 90% (입력) | (입력) | (입력) | (입력) |

*(After 실행 로그 / top 캡처 첨부)*

### 4-3. 근본 해결 제안 (선택)

- 임계 조정은 시간을 버는 미봉책이다. 근본적으로는 **CPU를 과점유하는 연산 로직**(불필요한 busy-loop, 비효율 알고리즘, 과도한 동시 작업)을 찾아 최적화해야 한다.
- 추적 방법: `top -H`로 어떤 스레드가 CPU를 점유하는지 확인 → 프로파일러(예: `py-spy`, `perf`)로 핫스팟 함수 식별 → 연산 분산/슬립 추가/알고리즘 개선.

---

*Reporter: KY Song · Codyssey26 / Task2 · 2026-06-16*
