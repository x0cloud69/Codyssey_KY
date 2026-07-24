from budget_app.decorators import log_call, timed, handle_errors


# --- 1. log_call + timed 겹쳐 쓰기 ---
@log_call
@timed
def greet(name: str) -> str:
    print(f"안녕, {name}")
    return "완료"


# --- 2. handle_errors: 일부러 에러 내기 ---
@handle_errors
def will_fail() -> None:
    raise ValueError("일부러 낸 에러")


# --- 3. handle_errors: 정상일 땐 그대로 통과 ---
@handle_errors
def divide(a: int, b: int) -> int:
    result = a // b
    print(f"{a} / {b} = {result}")
    return result


print("=== 1) 정상 함수 (로그 + 시간) ===")
value = greet("KY")
print("반환값:", value)

print("\n=== 2) 에러 나는 함수 (예외 처리) ===")
will_fail()
print("→ 프로그램이 안 죽고 여기까지 왔으면 handle_errors 성공")

print("\n=== 3) 인자 있는 함수도 잘 감싸지는지 ===")
divide(10, 2)      # 정상: 5
divide(10, 0)      # 에러: 0으로 나누기 → handle_errors가 잡아줌
print("→ 0으로 나눴는데도 안 죽었으면 성공")