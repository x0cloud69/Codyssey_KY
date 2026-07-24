from budget_app.service import BudgetService

svc = BudgetService()

#검색용 샘플 데이터
#svc.add_transaction(type="expense", date="2024-01-15", amount=15000, category="food", memo="점심 회식", tags=["meal"])
#svc.add_transaction(type="expense", date="2024-01-20", amount=8000, category="transport", memo="택시")
#svc.add_transaction(type="income",  date="2024-01-25", amount=3000000, category="salary", memo="월급")
#svc.add_transaction(type="expense", date="2024-02-03", amount=12000, category="food", memo="저녁")

print("===전체 (조건 없음) ===")
for t in svc.search():
    print(t.date, t.type, t.category,t.amount,t.memo)
    
print("\n=== category Food ====")
for t in svc.search(category="food"):
    print(t.date, t.category,t.memo)

print("\n=== 2024-01 기간 (from ~ to) ===")
for t in svc.search(date_from="2024-01-15", date_to="2024-01-21"):
    print(t.date, t.category,t.memo)

print("\n=== type=expense + 메모에 '회식' ===")
for t in svc.search(type="expense",q="회식"):
    print(t.date, t.category, t.type, t.memo)