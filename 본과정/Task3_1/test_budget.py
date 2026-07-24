from budget_app.service import BudgetService
from budget_app.repository import TransactionRepository

# 깔끔한 계산 위해 거래 비우고 시작
TransactionRepository().path.write_text("", encoding="utf-8")

svc = BudgetService()

# 2024-01 지출 데이터
svc.add_transaction(type="expense", date="2024-01-15", amount=150000, category="rent", memo="월세")
svc.add_transaction(type="expense", date="2024-01-18", amount=45000, category="food", memo="장보기")
svc.add_transaction(type="expense", date="2024-01-20", amount=20000, category="transport", memo="택시")

#예산 설정
svc.set_budget(month="2024-01", amount=5000000)
print("예산 5,000,000 설정")

s=svc.summary(month="2024-01",top=3)
print(f"\n총 지출: {s['total_expense']}원")
print(f"예산: {s['budget']}원 (사용률 {s['usage_rate']}%)")
print("초과 여부:", "초과!" if s["over_budget"] else "여유 있음")

# 예산을 낮춰서 초과 상황 만들기
svc.set_budget(month="2024-01", amount=100000)
s2 = svc.summary(month="2024-01")
print(f"\n예산을 100000으로 변경 (사용률 {s2['usage_rate']}%)")
print("초과 여부:", "초과!" if s2["over_budget"] else "여유 있음")

# 예산 없는 달
s3 = svc.summary(month="2024-03")
print(f"\n2024-03 예산:", s3["budget"], "/ 사용률:", s3["usage_rate"])

