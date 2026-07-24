from __future__ import annotations
import json ,os   # 파이썬 객체를 파일에 쓸수 있는 글자 (JSON)로 바꿔주는 도구 
from multiprocessing import Value
from pathlib import Path
from typing import Iterator # 하나씩 흘려보낸다 는 타입표시용
from .config import DATA_DIR, TRANSACTIONS_FILE, CATEGORIES_FILE, BUDGETS_FILE # 다른파일엣 경로와 Transaction을 빌려옴
from .models import Transaction


class TransactionRepository:
    def __init__(self, path: Path = TRANSACTIONS_FILE) -> None:
        self.path = path
        DATA_DIR.mkdir(parents=True, exist_ok=True)  #data 폴더가 없으면 만들어, 있으면 에러 내지말고 그냥 넘어감
        self.path.touch(exist_ok=True) # 파일이 없으면 빈 파일을 만들어 줌

    def add(self, tx: Transaction) -> None:
        line = json.dumps(tx.to_dict(), ensure_ascii=False) #Transaction 객체를 dict 로 변경하여 한줄짜리 글자로 변환 , 한글코드 그대로 저장
        with open(self.path, "a", encoding="utf-8") as f: # a (append모드) 맨끝에 이어붙이기
            f.write(line + "\n")

    def stream(self) -> Iterator[Transaction]:
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip() # 줄 끝 공백, 줄바꿈 제거
                if not line:
                    continue        # 빈줄이면 건너뜀
                data = json.loads(line)  # add에서 그자로 바꾼걸 다시 dict 로 되돌림
                yield Transaction.from_dict(data) # dict를 다시 Transaction 객체로 만들어서 하나 내보냄
                # return 은 값 하나 주고 함수가 완전히 끝남
                # yield 는 하나주고 잠깐 멈췄다가, 또 달라고 하면 이어서 줘

    def next_id(self) -> str:
        max_num = 0
        for tx in self.stream():
            if tx.id.startswith("TX-"):
                try:
                    max_num = max(max_num, int(tx.id[3:]))
                except ValueError:
                    continue
        return f"TX-{max_num + 1:06d}"
###################################################################
# update / delete 
# 원칙 : 1. 임시파일을 (transactions.jsonl.tmp) 만든다
#        2. 전체를 읽어서 delete 면 해당내용은 제외 하고 임시파일에 추가
#        3. 전체를 읽어서 update 내용은 해당내용을 수정 하여 임시파일에 추가
#        4. 임시 파일을 원본 파일에 rewrite 한다.
###################################################################
    def _rewrite(self, transaction: list[Transaction]) -> None:
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with open(tmp_path,"w",encoding="utf-8") as f:   #임시 파일에 쓰기
            for tx in transaction:
                f.write(json.dumps(tx.to_dict(),ensure_ascii=False)+ "\n")
        os.replace(tmp_path, self.path) # tmp 파일 내용을  원본파일로 overwrite
        
    def delete(self, tx_id: str) -> bool:
        all_tx = list(self.stream())   #스트리밍으로 전체 거래를 읽어서 리스트로 만듬
        remaining = [tx for tx in all_tx if tx.id != tx_id] # id 가 지울 대상이 아닌것만 리스트 
        if len(remaining) == len(all_tx): # 지울 id 가 없는지 확인 
            return False
        self._rewrite(remaining)
        return True
    
    def update(self,tx_id: str, **fields) -> bool: #**fields, 데코레이션의 **kwargs 와 같은 원리
        all_tx = list(self.stream())
        found = False
        for i, tx in enumerate(all_tx): #  리스트를 돌때 번호랑 같을 같이 
            if tx.id == tx_id:
                data = tx.to_dict()  # 기존 거래를 dict 로 변경
                data.update(fields)  # 넘어온 필드만 덮어쓰기 (update > 파이썬 내장 메서드)
                all_tx[i] = Transaction.from_dict(data) # 덮어쓴 dict로 새 거래 객체를 만듦. 
                found = True
                break
        if not found:
            return False
        self._rewrite(all_tx)
        return True
        
    
###################################################################
# 카테고리 관리
# 1. 카테고리를(categories.jsonl) 에 저장.조회,.삭제 하는 categoryStore
# 2. 파일이 비어 있으면 기본 카테고리(food, transport 등) 자동생성
# 3. 삭제시 "사용 중인 카테고리는 못 지우개" 막기
##################################################################

from .config import CATEGORIES_FILE
DEFAULT_CATEGORIES = ["food","transport","rent","salary","etc"]

class CategoryStore:
    def __init__(self, path: Path=CATEGORIES_FILE) -> None:
        self.path = path
        DATA_DIR.mkdir(parents=True,exist_ok=True)
        self.path.touch(exist_ok=True)
        if not self.list_all():
            for name in DEFAULT_CATEGORIES:
                self.add(name)
                
    def list_all(self) -> list[str]:
        result = []
        with open(self.path,"r",encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    result.append(json.loads(line)["name"])
        return result
    
    def exists(self, name: str) -> bool:
        return name in self.list_all()
    
    def add(self, name:str) -> bool:
        name = name.strip()
        if not name:
            raise ValueError("카레고리명은 비어 있을 수 없습니다")
        if self.exists(name):
            return False
        with open(self.path,"a",encoding="utf-8") as f:
            f.write(json.dumps({"name": name}, ensure_ascii=False)+ "\n")
        return True
    def remove(self,name: str) -> None:
        if not self.exists(name):
            raise ValueError(f"없는 카테고리 입니다: {name}")
        remaining = [n for n in self.list_all() if n!= name]
        with open(self.path, "w", encoding="utf-8") as f:
            for n in remaining:
                f.write(json.dump({"name":n}, ensure_ascill=False) + "\n")
                
###################################################################
# 예산 관리 : SUMMARY 에 "예산 대비 얼마 사용했는지 + 초과 경과"
# 1. budget set --month 2024-01 --amount 50000 으로 월 예산 저장
# 2. 예산도 영구 저장(파일로)
# 3. summary 실행 시 예산이 있으면 사용률(%)과 초과 경고 표시
##################################################################
class BudgetStore:
    def __init__(self,path: Path = BUDGETS_FILE) -> None:
        self.path = path
        DATA_DIR.mkdir(parents=True, exist_ok = True)
        self.path.touch(exist_ok=True)
        
    def _load(self) -> dict[str, int]:
        result: dict[str,int] = {}
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    result[data["month"]]=data["amount"]
        return result
    
    def set_budget(self, month: str, amount: int) -> None:
        if amount <= 0:
            raise ValueError("예산은 양의 정수 여야 합니다")
        budgets = self._load()
        budgets[month] = amount
        with open(self.path, "w", encoding ="utf-8") as f:
            for m,a in budgets.items():
                f.write(json.dumps({"month":m, "amount": a}, ensure_ascii=False)+"\n")
    
    def get_budget(self, month:str) -> int | None:
        return self._load().get(month)
    