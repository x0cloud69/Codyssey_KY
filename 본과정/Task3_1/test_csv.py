from budget_app.service import BudgetService
from budget_app.repository import TransactionRepository

# 거래 비우고 시작
TransactionRepository().path.write_text("", encoding="utf-8")

svc = BudgetService()

# 원본 데이터
svc.add_transaction(type="expense", date="2024-01-15", amount=15000, category="food", memo="점심", tags=["meal", "work"])
svc.add_transaction(type="income",  date="2024-01-25", amount=3000000, category="salary", memo="월급")
svc.add_transaction(type="expense", date="2024-02-03", amount=12000, category="food", memo="2월거")

# 1) export — 1월만 내보내기
count = svc.export_csv(out_path="export_test.csv", month="2024-01")
print(f"export 완료: {count}건")

print("\n--- export_test.csv 내용 ---")
with open("export_test.csv", "r", encoding="utf-8") as f:
    print(f.read())

# 2) import — 방금 내보낸 걸 다시 불러오기
result = svc.import_csv(in_path="export_test.csv")
print(f"import 결과: imported={result['imported']}, skipped={result['skipped']}")