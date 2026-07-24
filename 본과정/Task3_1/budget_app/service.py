from __future__ import annotations
from .models import Transaction
from .repository import TransactionRepository,CategoryStore, BudgetStore
import csv
from pathlib import Path

class BudgetService:
    def __init__(self) -> None:
        self.tx_repo = TransactionRepository()
        self.cat_store = CategoryStore()
        self.budget_store = BudgetStore()
        
    def add_transaction(self, type: str, date:str, amount: int,
                        category: str, memo:str="", tags:list[str] | None =None):
        if not self.cat_store.exists(category): # 카테고리 있는 지 검증 
            raise ValueError(                 
                f"등록되지 않은 카테고리 입니다 : {category}"
                f"(사용가능: {', '.join(self.cat_store.list_all())})"
            ) 
        new_id = self.tx_repo.next_id() # 새로운 번호 획득
        tx = Transaction(
            id = new_id, type=type, date=date, amount=amount,
            category=category, memo=memo, tags=tags or [],
        )
        self.tx_repo.add(tx)  # CLI 에서 입력한 내용 저장
        return new_id
    
    ################## 검색 함수 #####################
    # 1. 여러 조건으로 거래를 걸러내는 검색로직
    # 2. 조건은 여러 개를 동시에 검색 할 수 있어야 함
    # 결과는 최신순
    # stream 을 사용하여 파일을 한줄씩 흘려 처리 
    ##################################################
    def search(self, date_from: str | None = None, date_to:str | None = None,
               category: str | None = None, type: str | None = None,
               q: str | None=None, tag:str | None=None) -> list[Transaction]:
        result = []
        for tx in self.tx_repo.stream():
            if date_from is not None and tx.date < date_from:
                continue
            if date_to is not None and tx.date > date_to:
                continue
            if category is not None and tx.category != category:
                continue
            if type is not None and tx.type != type:
                continue
            if tag is not None and tag not in tx.tags:
                continue
            result.append(tx)
        result.sort(key=lambda at:at.date, reverse=True)
        return result
    
    def delete_transaction(self, tx_id: str) -> bool:
        return self.tx_repo.delete(tx_id)
    
    def update_transaction(self,tx_id : str, **fields) -> bool:
        if "category" in fields and not self.cat_store.exists(fields["category"]):
            raise ValueError(f"등록되지 않은 카테고리 입니다: {fields['category']}")
        return self.tx_repo.update(tx_id,**fields)
    
    ################### 월별 요약 ########################
    # summary --month 202401 처럼 월을 받아서:
    #    - 총수입, 총지출, 잔액(수입 - 지출)
    #    - 카테고리별 지출 합계 TOP N (--top 옵션)
    # 데이터 없는 달은 "데이터 없음"으로 명확히 처리
    #
    # 계산 순서
    # 1. 그달에 속하는 거래만 추출
    # 2. income 이면 총수입에, expense 총지출에 금액을 더해
    # 3. expense는 카테고리별로도 떠로 합계를 계산 (TOP N 을 뽑기위해)
    ######################################################
    
    def summary(self, month:str, top: int = 3) -> dict:
        total_income = 0
        total_expense = 0
        category_expense: dict[str, int] = {}
        count = 0
        
        for tx in self.tx_repo.stream():
            if not tx.date.startswith(month):  # 해당 월이 아니면 건너뜀
                continue
            count += 1
            if tx.type == "income":
                total_income += tx.amount
            else:
                total_expense += tx.amount
                category_expense[tx.category]=category_expense.get(tx.category,0) + tx.amount
                
        # 카테고리별 지출을 큰 금액순으로 정렬해서 상위 N개
        top_categories = sorted(
            category_expense.items(),
            key=lambda item:item[1],
            reverse=True,
        )[:top]
        
        # 예산 부분
        budget = self.budget_store.get_budget(month)
        if budget is not None and budget > 0:
            usage_rate = round(total_expense / budget * 100, 1)
            over_budget = total_expense > budget
        else:
            usage_rate = None
            over_budget = False
  
        return {
            "month": month,
            "count":count,
            "total_income":total_income,
            "total_expense": total_expense,
            "balance":total_income -total_expense,
            "top_categories": top_categories,
            "budget": budget,
            "usage_rate": usage_rate,
            "over_budget": over_budget,
        }

    def set_budget(self, month:str, amount:int)-> None:
        self.budget_store.set_budget(month, amount)
            
    ################### 가져오기 / 내보내기 ##################
    # export : 조건(월 또는 기간)에 맞는 거래를 CSV로 저장
    # import : CSV 를 읽어서 거래 일괄 등록 (처리건수 보고)
    # 고정 CSV 스키마 : date, type, category, amount, memo, tags
    # 공통 : UTF-8, 헤더 포함, tags 는 쉼표로 구분한 문자열
    ######################################################
    
    CSV_COLUMNS = ["date","type","category","amount","memo","tags"]
    
    def export_csv(self, out_path: str, month:str | None = None,
                   date_from: str | None = None, date_to : str | None=None) -> int:
        if month is not None:
            date_from = month + "-01"
            date_to   = month + "-31"
        rows = self.search(date_from=date_from, date_to=date_to)
        
        with open(out_path,"w",encoding="utf-8",newline="") as f: #newline 줄사이에 줄이 끼는 문제 해결
            writer = csv.DictWriter(f, fieldnames=self.CSV_COLUMNS)  # dict를 CSV 한줄로 바꿔주는 도구, fieldnames 로 열순서 지정
            writer.writeheader() # 첫줄에 헤더 자동 출력
            for tx in rows:
                writer.writerow({
                    "date":tx.date,
                    "type":tx.type,
                    "category":tx.category,
                    "amount":tx.amount,
                    "memo":tx.memo,
                    "tags":",".join(tx.tags)  # 리스트를 쉼표로 이어붙여 문자열로로 ["meal","work"]-> "meal,work"
                })
        return len(rows)
    
    def import_csv(self,in_path:str) -> dict:
        imported = 0
        skipped  = 0
        with open(in_path,"r",encoding="utf-8",newline="") as f:
            reader = csv.DictReader(f)   # CSV를 읽어서 각 줄을 dict로 전환, 
            for row in reader:
                try:
                    tags = row["tags"].split(",") if row.get("tags") else [] #문자열을 쉼표로 쪼개 리스트로 "meal,work" > ["meal","work"]
                    tags = [t.strip() for t in tags if t.strip()] # 각 태그의 공백 제거 
                    self.add_transaction(
                        type=row["type"].strip(),
                        date=row["date"].strip(),
                        amount=int(row["amount"]),
                        category=row["category"].strip(),
                        memo=row.get("memo","").strip(),
                        tags=tags,
                    )
                    imported +=1 
                except (ValueError, KeyError):
                    skipped += 1
        return {"imported":imported, "skipped":skipped}
     