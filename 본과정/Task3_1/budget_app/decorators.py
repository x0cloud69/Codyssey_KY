from __future__ import annotations  # 타입 힌들르 "글자"로 취급하게 만들어서, 아직 정의 안된 이름을 미리 써도 에러가 안나게
import functools # 포장 할때 원래 함수의 "이름표"를 지켜주는 함수
import time      # 시간을 재는 도구
from typing import Any, Callable # 타입 힌트용, Calllable 은 "함수" 라는 뜻, Any는 아무 타입니나. 

######################################################################
# 데코레이터의 공통 뼈대
######################################################################
#  def 포장지(func):                     >> 1. 감쌀 함수를 받는다.
#     @functools.wraps(func)
#     def wrapper(*args,**kwargs):       >> 2. 새 포장 함수를 만든다
#         (앞에서 먼가 함)
#         result = func(*args, **kwargs) >> 3.원래 함수를 실행 
#         (뒤에서 뭔가 함)
#         return result                  >> 4.원래 결과를 돌려줌
#     return wapper                      >> 5.포장된 함수를 내보낸다
######################################################################
# 데코레이터 함수 구분 방법
# 1. 함수를 인자로 받는다  >> def log_call(func)
# 2. 안에 또 다른 함수(wrapper)를 만들어서 반환 한다. 
#     def log_call(func)
#         def wrapper(*args, **kwargs):
#         ...
#         return func(*args, **kwargs)
#    return wrapper
# 3. @를 붙여서 사용한다
#    @log_call
#    def add():
#       ...
######################################################################

def log_call(func: Callable) -> Callable:
    @functools.wraps(func)   # 원래 함수의 이름표를 지켜주는 안전장치
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # *args : 이름표 없는 인자, kwargs : 이름표 있는 함수 
        print(f"[로그] {func.__name__} 시작")
        result = func(*args, **kwargs)
        print(f"[로그] {func.__name__} 끝")
        return result
    return wrapper

def timed(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"[시간] {func.__name__}: {elapsed:.2f}ms")
        return result
    return wrapper

def handle_errors(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs:Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(f"[오류] {e}")
            print("[힌트] 입력값을 확인해 주세요.")
        except FileNotFoundError as e:
            print(f"[오류] 파일을 찾을 수 없습니다: {e}")
            print("[힌트] data 폴더와 저장 파일이 있는지 확인 하세요.")
    return wrapper
    