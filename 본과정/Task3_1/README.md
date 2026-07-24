# budget_app — 콘솔 가계부

파일 기반 저장(JSONL)으로 수입/지출을 관리하는 콘솔 애플리케이션.
표준 라이브러리만 사용하며, 제너레이터 스트리밍 · 데코레이터 · 타입 힌트 · 모듈 분리를 적용했다.

## 1. 실행 방법

### 개발 환경
- Python 3.10 이상 (개발/테스트: 3.13)
- 외부 라이브러리 없음 (표준 라이브러리만 사용)

### 실행

```bash
python -m budget_app <command> [options]
```

모든 명령은 `--help`로 사용법을 확인할 수 있다.

```bash
python -m budget_app --help
python -m budget_app summary --help
```

### 종료 코드
- 정상 종료: `0`
- 오류 종료: `0`이 아닌 값 (`1`)

오류는 스택트레이스 대신 `[오류] 원인` + `[힌트] 해결 방법` 형태로 출력된다.

## 2. 저장 파일 위치 및 형식

기본 저장 폴더는 `./data`이며, 프로그램 최초 실행 시 폴더와 파일이 자동 생성된다.

| 파일 | 내용 | 형식 |
| --- | --- | --- |
| `data/transactions.jsonl` | 거래 내역 | JSONL |
| `data/categories.jsonl` | 카테고리 목록 | JSONL |
| `data/budgets.jsonl` | 월별 예산 | JSONL |

공통: UTF-8 인코딩, 한 줄 = JSON 객체 하나.

### 각 파일의 레코드 구조

**transactions.jsonl**

```json
{"id": "TX-000001", "type": "expense", "date": "2024-01-15", "amount": 15000, "category": "food", "memo": "점심", "tags": ["meal"]}
```

| 필드 | 필수 | 설명 |
| --- | --- | --- |
| id | Y | `TX-` + 6자리 일련번호 (자동 생성) |
| type | Y | `income` / `expense` |
| date | Y | `YYYY-MM-DD` |
| amount | Y | 양의 정수 |
| category | Y | 등록된 카테고리 |
| memo | N | 문자열 |
| tags | N | 문자열 배열 |

**categories.jsonl**

```json
{"name": "food"}
```

카테고리 파일이 비어 있으면 기본 카테고리(`food`, `transport`, `rent`, `salary`, `etc`)가 자동 생성된다.

**budgets.jsonl**

```json
{"month": "2024-01", "amount": 500000}
```

같은 월을 다시 설정하면 기존 값을 덮어쓴다.

## 3. 주요 명령 예시

### 거래 추가 (add) — 대화형

```
$ python -m budget_app add
=== 거래 추가 ===
날짜(YYYY-MM-DD): 2024-01-15
타입(income/expense): expense
카테고리: food
금액(양수): 15000
메모(선택): 점심
태그(쉼표로 구분, 없으면 엔터): meal
[저장 완료] id=TX-000012
```

### 거래 목록 (list)

```
$ python -m budget_app list --limit 3
TX-000012 | 2024-01-15 | expense | food | 15000 | 점심
TX-000011 | 2024-01-14 | income | salary | 3000000 | 월급
TX-000010 | 2024-01-12 | expense | transport | 20000 | 택시
```

`--limit` 기본값은 10. 목록은 최신순으로 출력되며, 파일 전체를 메모리에 올리지 않고 제너레이터로 스트리밍 처리한다.

### 거래 검색 (search)

```
$ python -m budget_app search --from 2024-01-01 --to 2024-01-31 --category food
$ python -m budget_app search --type expense --q 점심
$ python -m budget_app search --tag meal
```

| 옵션 | 설명 |
| --- | --- |
| `--from` / `--to` | 기간 (YYYY-MM-DD) |
| `--category` | 카테고리 |
| `--type` | `income` / `expense` |
| `--q` | 메모 키워드 |
| `--tag` | 태그 |

조건은 여러 개를 동시에 지정할 수 있으며, 지정하지 않은 조건은 무시된다.

### 월별 요약 (summary)

```
$ python -m budget_app summary --month 2024-01 --top 3
총 수입: 3000000원
총 지출: 215000원
잔액: 2785000원
예산: 500000원 (사용률 43.0%)

지출 TOP 3
1) rent 150000원
2) food 45000원
3) transport 20000원
```

- `--top` 기본값은 3
- 해당 월에 데이터가 없으면 `[2024-01] 데이터 없음` 출력
- 예산이 설정되어 있으면 사용률(%)이 함께 출력되며, 초과 시 경고 문구가 표시된다

### 예산 설정 (budget)

```
$ python -m budget_app budget set --month 2024-01 --amount 500000
[저장 완료] 2024-01 예산 500000원
```

### 카테고리 관리 (category)

```
$ python -m budget_app category list
- food
- transport
- rent
- salary
- etc

$ python -m budget_app category add
카테고리명: hobby
[저장 완료] category=hobby

$ python -m budget_app category remove
삭제할 카테고리명: food
[실패] 사용 중인 카테고리입니다 (3건). 삭제할 수 없습니다.
```

해당 카테고리를 사용하는 거래가 존재하면 삭제가 차단된다.

### 거래 수정 (update) — 옵션 방식

**본 프로그램의 update는 옵션 방식으로 고정한다.**

```
$ python -m budget_app update --id TX-000012 --amount 20000 --memo 수정됨
[수정 완료] id=TX-000012 → {'amount': 20000, 'memo': '수정됨'}
```

| 옵션 | 필수 | 설명 |
| --- | --- | --- |
| `--id` | Y | 수정할 거래 id |
| `--date` | N | 날짜 |
| `--type` | N | 타입 |
| `--category` | N | 카테고리 |
| `--amount` | N | 금액 |
| `--memo` | N | 메모 |

지정한 필드만 수정되며 나머지는 유지된다. 존재하지 않는 id는 `[실패] 없는 id입니다` 출력 후 종료 코드 1로 종료한다.

### 거래 삭제 (delete)

```
$ python -m budget_app delete --id TX-000012
[삭제 완료] id=TX-000012
```

존재하지 않는 id는 실패 메시지 출력 후 종료 코드 1로 종료한다.

### 내보내기 / 가져오기 (export / import)

```
$ python -m budget_app export --out export.csv --month 2024-01
[완료] export.csv (12 records)

$ python -m budget_app export --out export.csv --from 2024-01-01 --to 2024-03-31
[완료] export.csv (30 records)

$ python -m budget_app import --from import.csv
[완료] imported=5, skipped=0
```

export는 `--month` 또는 `--from`/`--to` 중 하나 이상을 필수로 받는다.
import 시 검증에 실패한 행(잘못된 날짜, 음수 금액, 미등록 카테고리 등)은 건너뛰고 `skipped`로 집계된다.

## 4. import / export CSV 스키마

공통: UTF-8, 헤더 포함.

| column | required | 설명 |
| --- | --- | --- |
| date | Y | YYYY-MM-DD |
| type | Y | income / expense |
| category | Y | 등록된 카테고리 |
| amount | Y | 양수 정수 |
| memo | N | 문자열 |
| tags | N | 쉼표(,) 구분 문자열 |

예시:

```csv
date,type,category,amount,memo,tags
2024-01-15,expense,food,15000,점심,meal
2024-01-25,income,salary,3000000,월급,
```

## 5. 프로젝트 구조

```
budget_app/
├── __init__.py       패키지 표시
├── __main__.py       진입점 (python -m budget_app)
├── cli.py            CLI 계층 — 명령 파싱, 대화형 입력, 출력
├── services.py       서비스 계층 — 업무 규칙, 집계, 예산 계산
├── repository.py     저장소 계층 — 파일 I/O, 제너레이터 스트리밍
├── models.py         모델 계층 — Transaction 데이터 구조와 검증
├── decorators.py     공통 관심사 — 로그 / 시간 측정 / 예외 처리
└── config.py         저장 경로 및 상수
data/
├── transactions.jsonl
├── categories.jsonl
└── budgets.jsonl
```

### 계층별 책임

| 계층 | 책임 |
| --- | --- |
| CLI | 명령 파싱(argparse), 사용자 입력/출력. 계산이나 저장은 하지 않는다 |
| 서비스 | 여러 저장소에 걸친 업무 규칙(등록된 카테고리만 허용 등), 집계, 예산 계산 |
| 저장소 | 파일 읽기/쓰기, 제너레이터 스트리밍, id 생성, 원자적 재작성 |
| 모델 | 데이터 구조 정의와 자체 검증(날짜 형식, 양수 금액, 허용 타입) |

## 6. 적용한 설계 요소

**제너레이터 스트리밍**
`TransactionRepository.stream()`은 `yield`로 거래를 한 건씩 내보낸다. 파일 전체를 메모리에 올리지 않으므로 데이터가 많아져도 메모리 사용량이 일정하다. `list`, `search`, `summary`가 모두 이 스트림 위에서 동작한다.

**데코레이터로 공통 관심사 분리**
`decorators.py`에 로그(`log_call`), 실행 시간 측정(`timed`), 예외 처리(`handle_errors`)를 분리했다. `cli.main()`에 `@handle_errors`를 적용해 모든 명령의 오류를 스택트레이스 대신 원인 + 힌트 형태로 출력한다.

**타입 힌트로 계약 명시**
함수 시그니처에 입출력 타입을 명시했다. 예를 들어 `def stream(self) -> Iterator[Transaction]`은 "거래를 하나씩 흘려보낸다"는 계약을, `def get_budget(self, month: str) -> int | None`은 "예산이 없을 수 있다"는 사실을 코드 자체로 드러낸다.

**저장 안정성**
update/delete는 임시 파일(`.tmp`)에 전체를 기록한 뒤 `os.replace()`로 원본과 교체하는 원자적 방식을 사용한다. 쓰기 도중 중단되어도 원본 데이터가 손상되지 않는다.