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
