from budget_app.models import Transaction
from budget_app.repository import TransactionRepository

repo = TransactionRepository()

new_id = repo.next_id()
tx = Transaction(id=new_id, type="expense", date="2024-01-15",
                 amount=15000, category="food", memo="점심", tags=["meal"])
repo.add(tx)
print("저장됨:", new_id)

print("--- 전체 목록 ---")
for t in repo.stream():
    print(t.id, t.date, t.type, t.category, t.amount, t.memo)