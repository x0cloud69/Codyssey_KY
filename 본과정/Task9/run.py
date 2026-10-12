"""
run.py : SQL 파일을 순서대로 실행하고, 쿼리별 실행 결과를 텍스트 파일로 저장하는 스크립트
==========================================================================================

[왜 필요한가]
  과제에서 "각 쿼리의 실행 결과를 스크린샷 또는 결과 텍스트로 남긴다"고 요구한다.
  쿼리 17개 + 보너스 9개를 하나씩 DB 도구에서 실행하고 캡처하는 대신,
  이 스크립트가 SQL 파일을 읽어 실행하고 결과를 표 형태의 텍스트로 자동 저장한다.
  (백엔드 프레임워크가 아니라, SQL을 실행해 주는 단순한 도구 스크립트이다.)

[사용법]
  python run.py

[실행 흐름]
  1) build_db()  : cafe.db 파일을 새로 만들고 schema.sql -> data.sql 실행
                   -> DBeaver 같은 도구로 열어 원본 데이터를 확인할 수 있다.
  2) run_file("queries.sql") : 메모리 DB에서 schema -> data -> queries 실행
                   -> results/queries/Q01.txt ~ Q17.txt, _all.txt 저장
  3) run_file("bonus.sql")   : 새 메모리 DB에서 schema -> data -> bonus 실행
                   -> results/bonus/B01.txt ~ B09.txt, _all.txt 저장

  2)와 3)을 서로 다른 DB에서 실행하는 이유:
  queries.sql 의 마지막 UPDATE/DELETE 가 데이터를 바꾸기 때문에,
  같은 DB에서 bonus.sql 을 이어서 실행하면 보너스 결과가 달라진다.
  매번 깨끗한 초기 데이터에서 시작해야 결과가 항상 같게 나온다.

[SQL 파일 작성 규칙 (이 스크립트가 블록을 나누는 기준)]
  -- [Q01] 설명            <- 이 줄부터 하나의 결과 블록이 시작된다 (Q 또는 B + 숫자)
  SELECT ...;              <- 블록 안의 SQL 문장(여러 개 가능)을 차례로 실행한다
  -- ===============       <- 섹션 구분선을 만나면 블록이 끝난다
"""
import re                 # 정규표현식: "-- [Q01] 설명" 형식의 마커 줄을 찾는 데 사용
import sqlite3            # 파이썬 표준 라이브러리에 포함된 SQLite 드라이버 (별도 설치 불필요)
import unicodedata        # 한글처럼 화면에서 2칸을 차지하는 문자를 판별하는 데 사용
from pathlib import Path  # 운영체제(Windows/Mac/Linux)에 상관없이 경로를 다루기 위해 사용

# 이 스크립트가 있는 폴더(Task9). 어느 위치에서 실행해도 SQL 파일을 찾을 수 있게 기준 경로로 쓴다.
BASE = Path(__file__).resolve().parent

# 실행 결과 텍스트를 저장할 최상위 폴더
RESULTS = BASE / "results"

# 결과 블록의 시작 줄을 찾는 패턴.
#   예) "-- [Q01] 기본 조회 | 판매 중인 메뉴 ..."
#   group(1) = "Q01"  (블록 id, 결과 파일 이름으로 사용)
#   group(2) = "기본 조회 | 판매 중인 메뉴 ..."  (쿼리 설명, 결과 파일 첫 줄에 기록)
MARKER = re.compile(r"^-- \[([QB]\d+)\] (.+)$")


# ---------------------------------------------------------------------------
# DB 연결 / 파일 읽기
# ---------------------------------------------------------------------------

def read_sql(name):
    """Task9 폴더에 있는 SQL 파일을 UTF-8 문자열로 읽어 온다. (한글 주석/데이터가 깨지지 않도록)"""
    return (BASE / name).read_text(encoding="utf-8")


def connect(path=":memory:"):
    """SQLite DB에 연결한다.

    path=":memory:" 이면 파일 없이 메모리에만 존재하는 임시 DB가 만들어지고,
    연결을 닫으면 사라진다. 결과 생성용으로는 매번 깨끗한 DB가 필요해서 이것을 쓴다.

    isolation_level=None : 자동 커밋(autocommit) 모드.
        파이썬 sqlite3 는 기본적으로 INSERT/UPDATE 전에 트랜잭션을 몰래 열어 두는데,
        트랜잭션 안에서는 PRAGMA foreign_keys 설정이 무시된다.
        자동 커밋으로 두면 각 문장이 실행 즉시 반영되어 SQL 도구에서 직접 실행할 때와 똑같이 동작한다.

    PRAGMA foreign_keys = ON :
        SQLite 는 기본값이 FK 검사 OFF 이고, 이 설정은 "연결마다" 따로 켜야 한다.
        켜지 않으면 존재하지 않는 고객 번호로 주문을 넣어도 에러가 나지 않는다.
    """
    conn = sqlite3.connect(path, isolation_level=None)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------------------------------------------------------------------
# 결과를 보기 좋은 표로 만드는 함수들
# ---------------------------------------------------------------------------

def display_width(text):
    """문자열이 화면(고정폭 글꼴)에서 차지하는 칸 수를 계산한다.

    len("김민준") 은 3 이지만 실제로는 영문 6글자만큼의 폭을 차지한다.
    east_asian_width 가 'W'(Wide) 또는 'F'(Fullwidth)인 문자(한글, 한자 등)는 2칸,
    나머지(영문, 숫자, 기호)는 1칸으로 계산해야 표의 세로줄이 맞는다.
    """
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def pad(text, width):
    """text 뒤에 공백을 붙여 화면 폭이 width 칸이 되도록 맞춘다. (왼쪽 정렬)"""
    return text + " " * (width - display_width(text))


def format_table(columns, rows):
    """SELECT 결과를 sqlite3 CLI / MySQL 과 비슷한 테두리 표 문자열로 만든다.

    예)
        +----+--------+
        | id | name   |
        +----+--------+
        | 1  | 김민준 |
        +----+--------+
        (1 rows)

    columns : 컬럼 이름 리스트   (cursor.description 에서 꺼낸 값)
    rows    : 결과 행 리스트     (cursor.fetchall() 결과, 각 행은 튜플)
    """
    # 1) 모든 값을 문자열로 바꾼다. 파이썬의 None 은 SQL 의 NULL 이므로 "NULL" 로 표시한다.
    cells = [["NULL" if v is None else str(v) for v in row] for row in rows]

    # 2) 컬럼마다 "제목과 모든 값 중 가장 넓은 폭"을 그 컬럼의 너비로 정한다.
    widths = [max([display_width(c)] + [display_width(r[i]) for r in cells])
              for i, c in enumerate(columns)]

    # 3) 가로 테두리 줄: 각 칸 양옆에 공백 1칸씩 들어가므로 너비 + 2 만큼 '-' 를 그린다.
    line = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    # 4) 테두리 - 제목 - 테두리 - 데이터 행들 - 테두리 - 행 수 순서로 조립한다.
    out = [line, "| " + " | ".join(pad(c, w) for c, w in zip(columns, widths)) + " |", line]
    out += ["| " + " | ".join(pad(v, w) for v, w in zip(r, widths)) + " |" for r in cells]
    out += [line, f"({len(rows)} rows)"]
    return "\n".join(out)


# ---------------------------------------------------------------------------
# SQL 파일을 블록 / 문장 단위로 나누는 함수들
# ---------------------------------------------------------------------------

def split_statements(sql):
    """여러 SQL 문장이 섞인 문자열을 문장 하나씩 리스트로 나눈다.

    단순히 ';' 로 자르면 문자열 안의 ';' 까지 잘릴 수 있으므로,
    SQLite 가 제공하는 sqlite3.complete_statement() 로 "문장이 완성되었는지" 판단한다.
    한 줄씩 버퍼에 쌓다가 완성된 문장이 되면 리스트에 넣고 버퍼를 비운다.
    """
    statements, buf = [], ""
    for line in sql.splitlines(keepends=True):
        buf += line
        if sqlite3.complete_statement(buf):
            if buf.strip():
                statements.append(buf.strip())
            buf = ""
    return statements


def strip_comments(stmt):
    """문장 앞뒤의 '--' 로 시작하는 주석 줄을 제거한다.

    결과 파일에는 실제로 실행한 SQL 만 깔끔하게 보이도록 하기 위함이다.
    (코드 뒤에 붙은 한 줄 주석, 예: "price INTEGER -- 가격" 은 SQL 의 일부로 그대로 둔다.)
    주석만 있고 SQL 이 없는 덩어리는 빈 문자열이 되어 실행을 건너뛴다.
    """
    return "\n".join(l for l in stmt.splitlines() if not l.strip().startswith("--")).strip()


def split_blocks(sql):
    """SQL 파일 전체를 '-- [Q01] 설명' 마커 기준으로 결과 블록 리스트로 나눈다.

    반환값: [(블록 id, 설명, 블록 SQL 본문), ...]
        예) [("Q01", "기본 조회 | ...", "SELECT id, name ...;"), ...]

    - 마커 줄을 만나면 새 블록을 시작한다.
    - 블록이 시작된 뒤의 줄은 그 블록의 본문에 추가한다.
    - '-- =====' 섹션 구분선을 만나면 현재 블록을 닫는다.
      (구분선 아래의 섹션 제목 주석이 앞 블록 결과에 섞이지 않게 하기 위함)
    - 첫 마커 이전의 줄(파일 머리말, PRAGMA 등)은 어떤 블록에도 속하지 않으므로 무시한다.
    """
    blocks, current = [], None
    for line in sql.splitlines():
        m = MARKER.match(line)
        if m:
            current = [m.group(1), m.group(2), []]
            blocks.append(current)
        elif current is not None:
            if line.startswith("-- ====="):
                current = None
            else:
                current[2].append(line)
    return [(bid, desc, "\n".join(body).strip()) for bid, desc, body in blocks]


# ---------------------------------------------------------------------------
# 실행
# ---------------------------------------------------------------------------

def run_block(conn, body):
    """블록 하나에 들어 있는 SQL 문장들을 차례로 실행하고, 실행 로그 텍스트를 만든다.

    결과 텍스트는 sqlite3 CLI 화면처럼 보이도록
      "sqlite> SQL 문장"  다음 줄에  "결과 표" 또는 "OK (n rows affected)" 또는 "ERROR: ..."
    형식으로 쌓는다.

    - SELECT / EXPLAIN 처럼 결과 행을 돌려주는 문장 : cursor.description 에 컬럼 정보가 있다 -> 표로 출력
    - INSERT / UPDATE / DELETE / CREATE 같은 문장    : description 이 None -> 영향받은 행 수 출력
    - 에러가 나는 문장 : 프로그램을 멈추지 않고 에러 메시지를 기록한다.
      보너스 과제의 "FK 에러 일부러 내 보기"(B03~B05)는 에러 메시지 자체가 결과물이기 때문이다.
    """
    parts = []
    for stmt in split_statements(body):
        sql = strip_comments(stmt)
        if not sql:
            continue
        # 여러 줄 SQL 은 두 번째 줄부터 "   ...> " 를 붙여 CLI 의 이어쓰기 프롬프트처럼 보이게 한다.
        parts.append("sqlite> " + sql.replace("\n", "\n   ...> "))
        try:
            cur = conn.execute(sql)
            if cur.description:
                cols = [d[0] for d in cur.description]  # description 의 각 항목 첫 번째 값이 컬럼 이름
                parts.append(format_table(cols, cur.fetchall()))
            else:
                # rowcount 는 DDL(CREATE 등)에서 -1 이 나오므로 0 으로 표시한다.
                parts.append(f"OK ({cur.rowcount if cur.rowcount >= 0 else 0} rows affected)")
        except sqlite3.Error as e:
            parts.append(f"ERROR: {e}")
        parts.append("")  # 문장 사이 빈 줄
    return "\n".join(parts)


def run_file(sql_file, out_dir):
    """깨끗한 메모리 DB에 스키마와 샘플 데이터를 넣은 뒤, sql_file 의 블록을 하나씩 실행해 저장한다.

    sql_file : 실행할 쿼리 파일 이름 (queries.sql / bonus.sql)
    out_dir  : 결과를 저장할 폴더 (results/queries, results/bonus)
    """
    # 결과 폴더를 만들고, 이전 실행 때 남은 .txt 파일은 지운다.
    # (쿼리를 지우거나 번호를 바꿨을 때 옛날 결과 파일이 남아 헷갈리지 않도록)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.txt"):
        old.unlink()

    # 메모리 DB 에 schema.sql -> data.sql 순서로 실행해 초기 상태를 만든다.
    # executescript() 는 여러 문장이 들어 있는 SQL 파일 전체를 한 번에 실행한다.
    conn = connect()
    conn.executescript(read_sql("schema.sql"))
    conn.executescript(read_sql("data.sql"))
    conn.execute("PRAGMA foreign_keys = ON")  # 혹시 스크립트 실행 중 설정이 바뀌었을 경우를 대비해 다시 켠다.

    summary = []
    for bid, desc, body in split_blocks(read_sql(sql_file)):
        # 결과 파일 머리말: "[Q01] 설명" + 구분선, 그 아래에 실행 로그
        text = f"[{bid}] {desc}\n{'=' * 70}\n\n{run_block(conn, body)}"
        (out_dir / f"{bid}.txt").write_text(text, encoding="utf-8")  # 블록별 파일 (Q01.txt ...)
        summary.append(text)

    # 모든 블록 결과를 한 파일로 모은 것 (한 번에 훑어보기 용)
    (out_dir / "_all.txt").write_text("\n\n".join(summary), encoding="utf-8")
    conn.close()
    print(f"{sql_file}: {len(summary)}개 결과 -> {out_dir.relative_to(BASE)}")


def build_db():
    """cafe.db 파일을 새로 만들고 schema.sql + data.sql 만 적용한다.

    queries.sql 은 적용하지 않으므로 UPDATE/DELETE 이전의 원본 데이터 상태가 유지된다.
    DBeaver 등에서 이 파일을 열어 직접 쿼리를 실행해 볼 수 있다.
    실행이 끝나면 테이블별 행 수를 출력해 "테이블당 10행 이상" 조건을 확인한다.
    """
    db = BASE / "cafe.db"
    db.unlink(missing_ok=True)  # 기존 파일이 있으면 지우고 새로 만든다 (재실행해도 항상 같은 상태)
    conn = connect(db)
    conn.executescript(read_sql("schema.sql"))
    conn.executescript(read_sql("data.sql"))
    for table in ["category", "customer", "menu", "orders", "order_item"]:
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<11} {n:>3} rows")
    conn.close()
    print(f"cafe.db 생성 완료 (SQLite {sqlite3.sqlite_version})")


# 이 파일을 직접 실행했을 때만 아래가 동작한다. (다른 파이썬 파일에서 import 할 때는 실행되지 않음)
if __name__ == "__main__":
    build_db()
    run_file("queries.sql", RESULTS / "queries")
    run_file("bonus.sql", RESULTS / "bonus")
