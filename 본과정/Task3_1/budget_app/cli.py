from __future__ import annotations
import argparse # 터미널에 친 명령어와 옵션을 해석 해주는 도구 상자
import sys

from .service import BudgetService
from .decorators import handle_errors

def cmd_add(svc: BudgetService, args) -> None:
    print("=== 거래 추가 ===")
    date = input("날짜(YYYY-MM-DD): ").strip()
    type_ = input("타입(income/expense): ").strip()
    category = input("카테고리: ").strip()
    amount = int(input("금액(양수): ").strip())
    memo = input("메모(선택): ").strip()
    tags_raw = input("태그(쉼표로 구분, 없으면 엔터): ").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    new_id = svc.add_transaction(type=type_, date=date, amount=amount,
                                 category=category, memo=memo, tags=tags)
    print(f"[저장 완료] id={new_id}")


def cmd_list(svc: BudgetService, args) -> None:
    rows = svc.search()[:args.limit]
    if not rows:
        print("거래가 없습니다.")
        return
    for tx in rows:
        print(f"{tx.id} | {tx.date} | {tx.type} | {tx.category} | {tx.amount} | {tx.memo}")


def cmd_summary(svc: BudgetService, args) -> None:
    s = svc.summary(month=args.month, top=args.top)
    if s["count"] == 0:
        print(f"[{args.month}] 데이터 없음")
        return
    print(f"총 수입: {s['total_income']}원")
    print(f"총 지출: {s['total_expense']}원")
    print(f"잔액: {s['balance']}원")
    if s["budget"] is not None:
        warn = " 예산 초과!" if s["over_budget"] else ""
        print(f"예산: {s['budget']}원 (사용률 {s['usage_rate']}%){warn}")
    print(f"\n지출 TOP {len(s['top_categories'])}")
    for rank, (cat, amount) in enumerate(s["top_categories"], start=1):
        print(f"{rank}) {cat} {amount}원")
        
def cmd_delete(svc:BudgetService, args) -> None:
    if svc.delete_transaction(args.id):
        print(f"[ 삭제완료] id={args.id}")
    else:
        print(f"[실패] 없는 id 입니다: {args.id}")
        sys.exit(1)

def cmd_update(svc:BudgetService, args) -> None:
    fields={}
    for key in ("data","type","category","amount","memo"):
        value = getattr(args,key)
        if value is not None:
            fields[key]=value
            
        if not fields:
            print("[안내] 수정할 항목을 하나 이상 지정하세요 (예: --amount 20000)")
            sys.exit(1)
            
        if svc.update_transaction(args.id,**fields):
            print(f"[수정 완료] id={args.id} -> {fields}")
        else:
            print(f"[실패] 없는 id 입니다: {args.id}")
            sys.exit(1)
            
def cmd_search(svc:BudgetService, args) -> None:
    rows = svc.search(date_from=getattr(args,"from"), date_to=args.to,
                      category=args.category, type=args.type,
                      q=args.q, tag=args.tag)
    if not rows:
        print("검색 결과가 없습니다.")
        return
    for tx in rows:
      print(f"{tx.id} | {tx.date} | {tx.type} | {tx.category} | {tx.amount} | {tx.memo}")
    print(f"\n총 {len(rows)}건")  
    
def cmd_budget(svc: BudgetService, args) -> None:
    svc.set_budget(month=args.month, amount=args.amount)
    print(f"[저장 완료] {args.month} 예산 {args.amount}원")
    
def cmd_category(svc:BudgetService, args) -> None:
    if args.action =="list":
        for name in svc.cat_store.list_all():
            print(f"- {name}")
    elif args.action == "add":
        name = input("카테고리명 : ").srtrip()
        if svc.cat_store.add(name):
            print(f"[저장완료] category={name}")
        else:
            print(f"[안네]이미 있는 카데고리 입니다: {name}")
    elif args.action == "remove":
        name = input("삭제할 카테고리명 : ").strip()
        used = svc.search(category=name)
        if used:
            print(f"[실패] 사용 중인 카테고리 입니다 ({len(used)}건). 삭제할 수 없습니다.")
            sys.exit(1)
        svc.cat_store.remove(name)
        print(f"[삭제 완료] category={name}")
        
def cmd_export(svc: BudgetService, args) -> None:
    if args.month is None and getattr(args, "from") is None:
       print("[오류] --month 또는 --from/--to 중 하나는 필수입니다")
       print("[힌트] 예: export --out out.csv --month 2024-01")
       sys.exit(1)
    n = svc.export_csv(out_path=args.out, month=args.month,
                       date_from=getattr(args,"from"), date_to=args.to)
    print(f"[완료] {args.out} ({n} records)")
    
def cmd_import(svc: BudgetService, args) -> None:
    r = svc.import_csv(in_path=getattr(args,"from"))
    print(f"[완료] imported={r['imported']}, skipped={r['skipped']}")

######################## argparse ###################################
# argparse.ArgumentParser(...)       해석기(파서) 하나 만듦
# .add_subparsers(...)               하위 명령 받는 창구 달기
# .add_parser("add")                 명령하나 등록
# .add_argument("--limit")           옵션 하나 등록
# .parse_args()                      실제입력을 해석
######################################################################

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="budget_app", description="콘솔 가계부")
    # prog = "budget_app"              >> 이 프로그램 이름은 budget_app 
    # decription = "콘솔 가계부"        >> 이 프로그램은 콘솔 가계부
    # 이둘은 --help 를 볼때 나타나는 정보
    sub = parser.add_subparsers(dest="command", required=True)
    # add_subparsers : 하위 명령(서브 커맨드)를 받는다
    # dest = "command"  : 어떤 명령이 왔는지를 args.command 에 담아둬라는 뜻, 나중에 main에서 args.command 를 보고 판단함.
    # required=True : 명령을 반드시 줘야 함. 

    sub.add_parser("add", help="거래 추가 (대화형)")

    p_list = sub.add_parser("list", help="거래 목록")
    p_list.add_argument("--limit", type=int, default=10)

    p_sum = sub.add_parser("summary", help="월별 요약")
    p_sum.add_argument("--month", required=True, help="YYYY-MM")
    p_sum.add_argument("--top", type=int, default=3)

    p_del = sub.add_parser("delete",help="거래삭제")
    p_del.add_argument("--id", required=True)
    
    p_up = sub.add_parser("update", help="거래 수정(옵션 방식)")
    p_up.add_argument("--id",required=True)
    p_up.add_argument("--date")
    p_up.add_argument("--type")
    p_up.add_argument("--category")
    p_up.add_argument("--amount", type=int)
    p_up.add_argument("--memo")
    
    p_search=sub.add_parser("search",help="거래 검색")
    p_search.add_argument("--from", dest="from")
    p_search.add_argument("--to")
    p_search.add_argument("--category")
    p_search.add_argument("--type")
    p_search.add_argument("--q", help="메모 키워드")
    p_search.add_argument("--tag")
    
    p_budget = sub.add_parser("budget", help="예산 설정")
    p_budget.add_argument("action", choices=["set"])
    p_budget.add_argument("--month",required=True)
    p_budget.add_argument("--amount",type=int, required=True)
    
    p_cat=sub.add_parser("category",help="카테고리 관리")
    p_cat.add_argument("action",choices=["add","list","removed"])
    
    p_exp = sub.add_parser("export", help="CSV 내보내기")
    p_exp.add_argument("--out",required=True)
    p_exp.add_argument("--month")
    p_exp.add_argument("--from", dest="from")
    p_exp.add_argument("--to")
    
    p_imp=sub.add_parser("import",help="CSV 가져오기")
    p_imp.add_argument("--from",dest="from",required=True)
    return parser


@handle_errors
def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    svc = BudgetService()

    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "summary": cmd_summary,
        "delete": cmd_delete,
        "update": cmd_update,
        "search": cmd_search,
        "budget": cmd_budget,
        "category": cmd_category,
        "export": cmd_export,
        "import": cmd_import,
        
    }
    commands[args.command](svc, args)
    return 0


#############  확인 방법 ##########################################
# python -m budget_app --help
# python -m budget_app category list
# python -m budget_app budget set --month 2024-01 --amount 500000
# python -m budget_app summary --month 2024-01
# python -m budget_app search --category food
# python -m budget_app search --from 2024-01-01 --to 2024-01-31
# python -m budget_app export --out out.csv --month 2024-01
# python -m budget_app import --from out.csv
#######################################################################