from budget_app.service import BudgetService
from budget_app.repository import TransactionRepository

# 깔끔한 계산 확인을 위해 거래 파일 비우고 시작
#TransactionRepository().path.write_text("", encoding="utf-8")

svc = BudgetService()
# 2024-01 데이터 심기
svc.add_transaction(type="income",  date="2024-01-25", amount=3000000, category="salary", memo="월급")
svc.add_transaction(type="expense", date="2024-01-15", amount=15000, category="food", memo="점심")
svc.add_transaction(type="expense", date="2024-07-18", amount=30000, category="food", memo="장보기")
svc.add_transaction(type="expense", date="2024-01-20", amount=20000, category="transport", memo="택시")
svc.add_transaction(type="expense", date="2024-07-05", amount=150000, category="rent", memo="월세")

s=svc.summary(month="2024-07",top=3)

print(f"=== {s['month']} 요약 (거래 {s['count']}건)===")
print(f"총 수입 : {s['total_income']}원")
print(f"총 지출 : {s['total_expense']}원")
print(f"잔액 : {s['balance']}원")
print(f"\n 지출 TOP {len(s['top_categories'])}")
for rank, (cat,amount) in enumerate(s['top_categories'], start=1):
    print(f"{rank} {cat} {amount}원")