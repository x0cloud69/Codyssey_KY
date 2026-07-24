from budget_app.service import BudgetService

svc = BudgetService()



#테스트 용 거래 하나 만들기
tx_id = svc.add_transaction(type="expense",date="2026-01-15",
                            amount=250000,category="food",memo="점심")
print("생성 : ", tx_id)

# 1) 수정 - 금액과 메모만 바꾸기
ok = svc.update_transaction(tx_id, amount=18000, memo="점심(수1정)")
print("수정 성공 ?",ok)

# 확인 
for t in svc.search():
    if t.id == tx_id:
        print("수정 결과 : ", t.id, t.amount, t.memo)
        
# 2) 없는 id 수정 시도
print("없는 id 수정 ?", svc.update_transaction("TX-999999",amount=1000))

# 3) 삭제
print("삭제 성공?", svc.delete_transaction(tx_id))

# 4) 없는 id 삭제 시도
#print("없는 id 삭제 ?", svc.delete_transaction("TX-999999"))