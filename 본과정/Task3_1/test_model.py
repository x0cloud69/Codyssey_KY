from budget_app.models import Transaction

t = Transaction(id="TX-000001", type="expense", date="2024-01-15",
                amount=15000, category="food", memo="점심", tags=["meal"])
print("정상 생성:", t.to_dict())

# 일부러 틀린 날짜 → 여기서 에러가 나야 정상
try:
    Transaction(id="TX-x", type="expense", date="2024-12-10",
                amount=1000, category="food")
except ValueError as e:
    print("검증 작동 확인:", e)