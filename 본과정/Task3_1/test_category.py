from budget_app.repository import CategoryStore
from budget_app.service import BudgetService

# 1) 기본 카테고리 자동 생성
store = CategoryStore()
print("카테고리 목록 : ",store.list_all()) 

# 2) 서비스로 거래 추가 - 등록된 카테고리
svc = BudgetService()
new_id = svc.add_transaction(type="expense", date ="2026-07-15",
                             amount=150000, category="food", memo="점심")
print("거래 저장됨: ", new_id)