# Mini NPU Simulator

MAC(Multiply-Accumulate) 연산 기반 패턴 판별 시뮬레이터

---

## 실행 방법

```bash
# data.json 파일이 main.py와 같은 폴더에 있어야 합니다.
python main.py
```

### 모드 선택

| 모드 | 설명 |
|------|------|
| 1 | 3×3 필터 2개(A, B)와 패턴을 직접 입력 |
| 2 | data.json에서 필터/패턴 로드 후 일괄 판정 |

### 모드 1 입력 예시 (십자가 vs X)

```
필터 A (십자가):   필터 B (X):      패턴 (X):
0 1 0              1 0 1            1 0 1
1 1 1              0 1 0            0 1 0
0 1 0              1 0 1            1 0 1

→ A 점수: 1.0 / B 점수: 5.0 / 판정: B
```

---

## 구현 요약

### 라벨 정규화 방식

프로그램 내부에서 사용하는 표준 라벨은 `Cross`, `X` 두 가지입니다.
`normalize_label()` 함수에서 아래 규칙으로 변환합니다.

| 입력값 | 표준 라벨 |
|--------|-----------|
| `+`, `cross` | `Cross` |
| `x` | `X` |

data.json의 `expected` 필드와 필터 키 모두 이 함수를 통해 정규화됩니다.
정규화 없이 단순 문자열 비교를 하면 `'+'`와 `'Cross'`가 다른 값으로 처리되어
올바른 PASS/FAIL 판정이 불가능하기 때문입니다.

### MAC 연산 구현

```python
def mac_operation(pattern, filter_mat):
    n = len(pattern)
    score = 0.0
    for i in range(n):
        for j in range(n):
            score += pattern[i][j] * filter_mat[i][j]
    return score
```

NumPy 없이 이중 반복문으로 직접 구현합니다.
연산 횟수는 N×N = N² 번이며, 이것이 시간 복잡도 O(N²)의 근거입니다.

### 동점 처리 정책 (epsilon)

```python
EPSILON = 1e-9

if abs(score_cross - score_x) < EPSILON:
    return 'UNDECIDED'
```

부동소수점 연산은 0.1 + 0.2 = 0.30000000000000004 처럼
미세한 오차를 포함합니다. 두 점수를 `==`로 비교하면
실질적으로 같은 값이 다르다고 판정될 수 있습니다.
따라서 차이가 1e-9 미만이면 동점(UNDECIDED)으로 처리합니다.

---

## 결과 리포트

### FAIL 케이스 원인 분석

data.json에는 총 8개의 테스트 케이스가 포함됩니다.

**FAIL 케이스: size_5_3 (동점 UNDECIDED)**

- 패턴이 모든 값이 0.5인 균등 행렬입니다.
- Cross 필터의 1 위치: 9개, X 필터의 1 위치: 9개 (5×5 기준 5+5-1=9)
- MAC(균등패턴, Cross) = 0.5 × 9 = 4.5
- MAC(균등패턴, X) = 0.5 × 9 = 4.5
- 두 점수가 동일하여 UNDECIDED 판정 → expected가 'x'이므로 FAIL
- **원인 분류: 데이터 문제** — 어느 쪽으로도 분류 불가능한 중립 패턴

**FAIL 케이스: size_5_4 (크기 불일치)**

- 패턴이 3×3인데 대응 필터는 5×5입니다.
- 스키마 불일치로 MAC 연산 자체를 수행할 수 없습니다.
- **원인 분류: 스키마/데이터 문제** — 입력 데이터 크기 오류

**나머지 6개 케이스가 PASS인 이유**

- 순수한 Cross 또는 X 패턴은 대응 필터와 정확히 일치하고 반대 필터와는 중심(1개)만 겹칩니다.
- 예) 5×5 Cross 패턴: MAC(Cross필터)=9, MAC(X필터)=1 → 명확히 Cross 판정
- 라벨 정규화 덕분에 `'+'`와 `'Cross'`가 동일하게 처리되어 문자열 불일치 FAIL이 0건입니다.
- epsilon 정책 덕분에 정수값 기반 패턴에서는 부동소수점 오차가 판정에 영향을 주지 않습니다.

### 시간 복잡도 분석: O(N²)

MAC 연산의 핵심은 N×N 크기의 두 배열을 위치별로 곱하고 더하는 것입니다.
총 연산 횟수는 정확히 N² 번으로, 패턴 크기가 2배가 되면 연산량은 4배 증가합니다.

```
N=3  → 9번
N=5  → 25번   (3배 이상)
N=13 → 169번  (약 7배)
N=25 → 625번  (약 70배 vs N=3)
```

아래는 실측 성능 표(환경마다 다를 수 있음)입니다.

| 크기    | 평균 시간(ms) | 연산 횟수(N²) |
|---------|-------------|-------------|
| 3×3     | ~0.001      | 9           |
| 5×5     | ~0.003      | 25          |
| 13×13   | ~0.018      | 169         |
| 25×25   | ~0.065      | 625         |

측정값이 N²에 비례하여 증가하는 것을 확인할 수 있으며, 이는 O(N²) 복잡도를 실증합니다.
실제 AI 모델(수백×수백 필터 수천 개)에서는 이 연산이 수억~수조 회 발생하므로
GPU/NPU의 병렬 처리가 필수적입니다.

### 보너스: 1차원 최적화

2차원 배열을 1차원으로 펼쳐(flatten) MAC 연산을 수행하면
내부 인덱싱 오버헤드가 줄어 작은 크기에서 약간의 성능 향상을 볼 수 있습니다.
단, Python 수준의 최적화 효과는 크지 않으며 실제 NPU는 하드웨어 수준의 병렬 처리로 이 문제를 해결합니다.

---

## 파일 구조

```
├── main.py       # 메인 실행 파일
├── data.json     # 테스트 필터/패턴 데이터
└── README.md     # 본 문서
```
![모드1 화면](모드1.jpg)


```
"""
Mini NPU Simulator
MAC(Multiply-Accumulate) 연산 기반 패턴 판별 시뮬레이터
"""

import json
import time


# ─────────────────────────────────────────────
# 1. MAC 연산 (외부 라이브러리 금지 - 반복문 직접 구현)
# ─────────────────────────────────────────────

def mac_operation(pattern: list, filter_mat: list) -> float:
    """
    MAC(Multiply-Accumulate) 연산
    같은 위치의 값을 곱하고 모두 더한다.
    """
    n = len(pattern)
    score = 0.0
    for i in range(n):
        for j in range(n):
            score += pattern[i][j] * filter_mat[i][j]
    return score


def measure_mac(pattern: list, filter_mat: list, repeat: int = 10):
    """MAC 연산을 repeat회 반복 측정 후 (마지막 점수, 평균 시간ms) 반환"""
    times = []
    score = 0.0
    for _ in range(repeat):
        start = time.perf_counter()
        score = mac_operation(pattern, filter_mat)
        end = time.perf_counter()
        times.append((end - start) * 1000)
    avg_ms = sum(times) / len(times)
    return score, avg_ms


# ─────────────────────────────────────────────
# 2. 라벨 정규화
# ─────────────────────────────────────────────

def normalize_label(label: str) -> str:
    """
    다양한 형태의 라벨을 표준 라벨로 변환한다.
      '+', 'cross' → 'Cross'
      'x'          → 'X'
    """
    normalized = label.strip().lower()
    if normalized in ['+', 'cross']:
        return 'Cross'
    elif normalized == 'x':
        return 'X'
    return label  # 알 수 없는 라벨은 원본 반환


# ─────────────────────────────────────────────
# 3. 점수 비교 (epsilon 기반 동점 처리)
# ─────────────────────────────────────────────

EPSILON = 1e-9

def judge(score_cross: float, score_x: float) -> str:
    """
    두 점수를 비교해 Cross / X / UNDECIDED 반환.
    |score_cross - score_x| < EPSILON 이면 동점(UNDECIDED).
    """
    if abs(score_cross - score_x) < EPSILON:
        return 'UNDECIDED'
    return 'Cross' if score_cross > score_x else 'X'


# ─────────────────────────────────────────────
# 4. 패턴 생성기 (보너스)
# ─────────────────────────────────────────────

def generate_cross(n: int) -> list:
    """n×n 십자가 패턴 생성: 가운데 행/열이 1"""
    mat = [[0] * n for _ in range(n)]
    mid = n // 2
    for i in range(n):
        mat[mid][i] = 1
        mat[i][mid] = 1
    return mat


def generate_x(n: int) -> list:
    """n×n X 패턴 생성: 두 대각선이 1"""
    mat = [[0] * n for _ in range(n)]
    for i in range(n):
        mat[i][i] = 1
        mat[i][n - 1 - i] = 1
    return mat


# ─────────────────────────────────────────────
# 5. 1차원 최적화 (보너스: 메모리 접근 단순화)
# ─────────────────────────────────────────────

def flatten(mat: list) -> list:
    """2차원 배열 → 1차원 배열"""
    return [val for row in mat for val in row]


def mac_operation_flat(pattern_flat: list, filter_flat: list) -> float:
    """1차원 배열 기반 MAC 연산"""
    score = 0.0
    for a, b in zip(pattern_flat, filter_flat):
        score += a * b
    return score


# ─────────────────────────────────────────────
# 6. 콘솔 입력 처리 (모드 1)
# ─────────────────────────────────────────────

def input_matrix(size: int, name: str) -> list:
    """
    콘솔에서 size×size 행렬을 입력받는다.
    오류 시 안내 메시지 출력 후 재입력 유도.
    """
    print(f"{name} ({size}줄 입력, 공백 구분)")
    matrix = []
    while len(matrix) < size:
        try:
            line = input(f"  {len(matrix)+1}행: ")
            nums = line.split()
            if len(nums) != size:
                print(f"  [오류] 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요. "
                      f"(입력: {len(nums)}개)")
                continue
            matrix.append([float(x) for x in nums])
        except ValueError:
            print(f"  [오류] 숫자만 입력하세요.")
    return matrix


def print_matrix(mat: list, label: str = ""):
    """행렬을 보기 좋게 출력"""
    if label:
        print(f"  [{label}]")
    for row in mat:
        print("  " + "  ".join(f"{v:4.1f}" for v in row))


# ─────────────────────────────────────────────
# 7. 성능 분석 출력
# ─────────────────────────────────────────────

def run_performance_analysis(sizes: list):
    """크기별 MAC 연산 시간 측정 (10회 평균)"""
    print("\n#---------------------------------------")
    print("# 성능 분석 (평균/10회 반복)")
    print("#---------------------------------------")
    print(f"{'크기':<10}  {'평균 시간(ms)':<18}  {'연산 횟수(N²)'}")
    print("-" * 48)

    for n in sizes:
        cross = generate_cross(n)
        # 연산 시간만 측정 (I/O 제외)
        _, avg_ms = measure_mac(cross, cross, repeat=10)
        print(f"  {n}×{n:<7}  {avg_ms:<18.6f}  {n*n}")


# ─────────────────────────────────────────────
# 8. 모드 1: 사용자 입력 (3×3)
# ─────────────────────────────────────────────

def mode1():
    print("\n#----------------------------------------")
    print("# [1] 필터 입력")
    print("#----------------------------------------")
    filter_a = input_matrix(3, "필터 A")
    print()
    filter_b = input_matrix(3, "필터 B")

    print("\n  ✓ 필터 저장 확인:")
    print_matrix(filter_a, "필터 A")
    print_matrix(filter_b, "필터 B")

    print("\n#---------------------------------------")
    print("# [2] 패턴 입력")
    print("#---------------------------------------")
    pattern = input_matrix(3, "패턴")
    print("\n  ✓ 패턴 저장 확인:")
    print_matrix(pattern, "패턴")

    print("\n#---------------------------------------")
    print("# [3] MAC 결과")
    print("#---------------------------------------")

    score_a, time_a = measure_mac(pattern, filter_a, repeat=10)
    score_b, time_b = measure_mac(pattern, filter_b, repeat=10)
    avg_time = (time_a + time_b) / 2

    print(f"  A 점수: {score_a:.16f}")
    print(f"  B 점수: {score_b:.16f}")
    print(f"  연산 시간(평균/10회): {avg_time:.6f} ms")

    result = judge(score_a, score_b)
    if result == 'UNDECIDED':
        print(f"  판정: 판정 불가 (|A-B| = {abs(score_a-score_b):.2e} < {EPSILON:.0e})")
    else:
        print(f"  판정: {result}")

    # 3×3 성능 분석 포함
    run_performance_analysis([3])


# ─────────────────────────────────────────────
# 9. 모드 2: data.json 분석
# ─────────────────────────────────────────────

def mode2():
    # ── JSON 로드 ──────────────────────────────
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("  [오류] data.json 파일을 찾을 수 없습니다.")
        return
    except json.JSONDecodeError as e:
        print(f"  [오류] data.json 파싱 실패: {e}")
        return

    # ── 필터 로드 & 라벨 정규화 ───────────────
    print("\n#---------------------------------------")
    print("# [1] 필터 로드")
    print("#---------------------------------------")

    filters = {}  # { 'size_5': {'Cross': [...], 'X': [...]} }

    for size_key, filter_dict in data.get('filters', {}).items():
        cross_mat = None
        x_mat = None
        for fkey, fval in filter_dict.items():
            norm = normalize_label(fkey)
            if norm == 'Cross':
                cross_mat = fval
            elif norm == 'X':
                x_mat = fval

        if cross_mat is not None and x_mat is not None:
            filters[size_key] = {'Cross': cross_mat, 'X': x_mat}
            print(f"  ✓ {size_key} 필터 로드 완료 (Cross, X)")
        else:
            missing = []
            if cross_mat is None: missing.append('Cross')
            if x_mat is None:     missing.append('X')
            print(f"  ✗ {size_key} 필터 로드 실패: {', '.join(missing)} 키 없음")

    # ── 패턴 분석 ─────────────────────────────
    print("\n#---------------------------------------")
    print("# [2] 패턴 분석 (라벨 정규화 적용)")
    print("#---------------------------------------")

    total, passed, failed = 0, 0, 0
    fail_cases = []

    for pkey, pval in data.get('patterns', {}).items():
        total += 1
        print(f"\n  --- {pkey} ---")

        # 키에서 크기 N 추출: size_5_1 → 5
        parts = pkey.split('_')
        try:
            n = int(parts[1])
        except (IndexError, ValueError):
            msg = f"키 파싱 실패 ({pkey})"
            print(f"  [FAIL] {msg}")
            failed += 1
            fail_cases.append((pkey, msg))
            continue

        size_key = f"size_{n}"
        if size_key not in filters:
            msg = f"대응 필터 없음 ({size_key})"
            print(f"  [FAIL] {msg}")
            failed += 1
            fail_cases.append((pkey, msg))
            continue

        filter_cross = filters[size_key]['Cross']
        filter_x     = filters[size_key]['X']
        pattern      = pval.get('input', [])
        expected_raw = str(pval.get('expected', ''))
        expected     = normalize_label(expected_raw)

        # 크기 검증
        if len(pattern) != n or any(len(row) != n for row in pattern):
            actual_rows = len(pattern)
            actual_cols = len(pattern[0]) if pattern else 0
            msg = (f"크기 불일치 (패턴: {actual_rows}×{actual_cols}, "
                   f"필터: {n}×{n})")
            print(f"  [FAIL] {msg}")
            failed += 1
            fail_cases.append((pkey, msg))
            continue

        # MAC 연산
        score_cross = mac_operation(pattern, filter_cross)
        score_x     = mac_operation(pattern, filter_x)

        print(f"  Cross 점수: {score_cross:.16f}")
        print(f"  X     점수: {score_x:.16f}")

        decision = judge(score_cross, score_x)

        # PASS / FAIL 판정
        if decision == 'UNDECIDED':
            result = 'FAIL'
            reason = f"동점(UNDECIDED) — |diff|={abs(score_cross-score_x):.2e}"
            failed += 1
            fail_cases.append((pkey, reason))
        elif decision == expected:
            result = 'PASS'
            passed += 1
        else:
            result = 'FAIL'
            reason = f"판정({decision}) ≠ expected({expected})"
            failed += 1
            fail_cases.append((pkey, reason))

        print(f"  판정: {decision} | expected: {expected} | {result}")

    # ── 성능 분석 ─────────────────────────────
    run_performance_analysis([3, 5, 13, 25])

    # ── 결과 요약 ─────────────────────────────
    print("\n#---------------------------------------")
    print("# [4] 결과 요약")
    print("#---------------------------------------")
    print(f"  총 테스트: {total}개")
    print(f"  통과    : {passed}개")
    print(f"  실패    : {failed}개")

    if fail_cases:
        print("\n  실패 케이스:")
        for case_id, reason in fail_cases:
            print(f"    - {case_id}: {reason}")
    else:
        print("\n  ✓ 모든 케이스 통과")

    print("\n  (상세 원인 분석 및 복잡도 설명은 README.md 참고)")

    # ── 보너스: 1차원 최적화 비교 ─────────────
    print("\n#---------------------------------------")
    print("# [보너스] 2D vs 1D 최적화 성능 비교")
    print("#---------------------------------------")
    print(f"{'크기':<10}  {'2D(ms)':<14}  {'1D(ms)':<14}  차이")
    print("-" * 52)

    for n in [5, 13, 25]:
        pat = generate_cross(n)
        flt = generate_cross(n)

        # 2D 측정
        _, t2d = measure_mac(pat, flt, repeat=10)

        # 1D 측정
        pat_flat = flatten(pat)
        flt_flat = flatten(flt)
        times_1d = []
        for _ in range(10):
            s = time.perf_counter()
            mac_operation_flat(pat_flat, flt_flat)
            e = time.perf_counter()
            times_1d.append((e - s) * 1000)
        t1d = sum(times_1d) / len(times_1d)

        diff = t2d - t1d
        sign = "↓ 빠름" if diff > 0 else "↑ 느림"
        print(f"  {n}×{n:<7}  {t2d:<14.6f}  {t1d:<14.6f}  {sign}")


# ─────────────────────────────────────────────
# 10. 메인
# ─────────────────────────────────────────────

def main():
    print("=" * 42)
    print("       Mini NPU Simulator")
    print("=" * 42)
    print("\n[모드 선택]")
    print("  1. 사용자 입력 (3×3)")
    print("  2. data.json 분석")

    while True:
        choice = input("\n선택: ").strip()
        if choice == '1':
            mode1()
            break
        elif choice == '2':
            mode2()
            break
        else:
            print("  [오류] 1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()

```
