# AI 기반 Git 커밋/PR 자동 생성기 (실습)

`git status`, `git diff` 결과를 AI API(Anthropic Claude)에 넘겨 **커밋 메시지**와 **PR 초안**을 만들어 주는 Python CLI 도구입니다. 결과는 터미널에 출력만 하며, 실제 커밋·push·PR 생성은 하지 않습니다.

## 동작 흐름

1. `git status`로 변경 파일 목록과 현재 브랜치를 수집합니다.
2. `git diff`로 변경 내용을 수집합니다.
3. (선택) `--safe-mode`로 민감정보를 마스킹하고 diff 분량을 제한합니다.
4. 양식과 규칙을 담은 프롬프트와 함께 AI API를 **1회** 호출합니다.
5. 응답을 길이/형식 규칙에 맞게 검증·후처리한 뒤 구분선과 함께 출력합니다.

## 설치

- Python 3.10 이상, Git
- 외부 패키지 없이 표준 라이브러리만 사용하므로 `pip install`이 필요 없습니다.

```bash
git clone <이 리포지토리 주소>
cd <리포지토리 폴더>
```

## 환경변수(API Key) 설정

API Key는 `AI_API_KEY` 환경변수로만 읽습니다. 코드나 파일에 적지 마세요.

```powershell
# Windows PowerShell
$env:AI_API_KEY="YOUR_KEY"
```

```bash
# macOS / Linux / Git Bash
export AI_API_KEY="YOUR_KEY"
```

## 실행 방법

Git이 초기화된 프로젝트 폴더에서 실행합니다.

```bash
python main.py commit            # 커밋 메시지 생성
python main.py pr                # PR 제목/본문 초안 생성
python main.py pr --base main    # main 브랜치와 비교한 diff로 PR 초안 생성
python main.py commit --safe-mode
python main.py commit --dry-run  # API 호출 없이 전송될 프롬프트만 확인
```

### 옵션

| 옵션 | 기본값 | 설명 |
| --- | --- | --- |
| `--model` | `claude-haiku-4-5` | 사용할 모델 |
| `--temperature` | `0.2` | 0.0~1.0. 낮을수록 일관되고, 높을수록 표현이 다양해집니다 |
| `--max-tokens` | `800` | 응답 최대 길이. 너무 작으면 결과가 중간에 잘립니다 |
| `--safe-mode` | 꺼짐 | 민감정보 마스킹 + diff 제한 |
| `--base` | 없음 | (pr 전용) 비교 기준 브랜치 |
| `--dry-run` | 꺼짐 | API를 호출하지 않고 프롬프트만 출력 |

## 출력 예시

> 아래 문구는 예시이며, 실제 결과는 변경 내용에 따라 달라집니다.

### 커밋 메시지

```text
[INFO] Git status 수집 완료: 3개 파일 변경 감지
[INFO] Git diff 수집 완료: 128줄
[INFO] AI API 요청 중... (model=claude-haiku-4-5, temperature=0.2, max_tokens=800)
[INFO] AI API 호출 횟수: 1회
[DONE] 커밋 메시지 생성 완료

--- Commit Message ---
feat: Git 변경 사항 기반 커밋 메시지 자동 생성 기능 추가

- main.py에 git status/diff 수집 로직 추가
- API Key 미설정 시 안내 메시지 출력
----------------------
```

### PR 초안

```text
[INFO] 현재 브랜치: feature/commit-pr-generator
[INFO] Git status 수집 완료: 3개 파일 변경 감지
[INFO] Git diff 수집 완료: 128줄
[INFO] AI API 요청 중... (model=claude-haiku-4-5, temperature=0.2, max_tokens=800)
[INFO] AI API 호출 횟수: 1회
[DONE] PR 초안 생성 완료

--- PR Title ---
feat: 커밋/PR 자동 생성 기능 추가
----------------

--- PR Body ---
## Why
- 커밋 메시지와 PR 설명 작성에 드는 시간을 줄이기 위해

## What
- git status, git diff 결과를 AI 입력으로 전달하는 로직 추가
- commit / pr 명령 구현

## How to Test
- python main.py commit
- python main.py pr
---------------
```

### 오류/예외 상황

```text
[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.
[ERROR] AI API 호출에 실패했습니다: HTTP 401 인증 실패(API Key를 확인하세요): ...
[INFO] 변경 사항이 없습니다. 커밋 메시지를 생성하지 않고 종료합니다.
```

## 출력 형식 검증(후처리)

AI 응답은 재호출 없이 후처리로 규칙에 맞춥니다. 고친 부분은 `[WARN]`으로 알려 줍니다.

| 대상 | 규칙 | 어겼을 때 |
| --- | --- | --- |
| 커밋 제목 | 50자 이내 권장, 최대 72자 | 72자 초과분을 잘라내고, 50자 초과 시 경고 |
| PR 제목 | 최대 80자 | 80자 초과분을 잘라냄 |
| PR 본문 | Why / What / How to Test 헤더 + 섹션별 불릿 1개 이상 | 빠진 섹션을 추가하고, 불릿이 없으면 불릿 형식으로 변환 |

## 주의사항

### 민감정보

`git diff`에는 API Key, 이메일 같은 민감정보가 섞일 수 있고, 이 내용은 외부 AI API로 전송됩니다. 공개하면 안 되는 내용이 있을 수 있으면 `--safe-mode`를 쓰세요.

- **마스킹**: API Key 형태(`sk-...`, `AIza...`, `AKIA...`, `ghp_...`), Bearer 토큰, `password=`/`secret=`/`token=` 값, 이메일, 휴대폰 번호를 `[MASKED_...]`로 바꿉니다.
- **전송 제한**: diff를 최대 10개 파일, 200줄까지만 보냅니다.

정규표현식 기반이라 모든 민감정보를 잡아내지는 못합니다. `--dry-run`으로 실제 전송될 내용을 먼저 확인할 수 있습니다.

### 비용/요청 횟수

- `commit`, `pr` 명령은 실행당 AI API를 1회만 호출하고, 호출 횟수를 로그에 출력합니다.
- diff가 크면 입력 토큰 비용이 늘어납니다. 큰 변경은 `--safe-mode`로 분량을 줄이거나 커밋을 나눠서 실행하세요.

### 결과 검토

생성된 문구는 초안입니다. 반드시 내용을 검토하고 필요한 부분을 고친 뒤 사용하세요.

---

## 실습 기록

직접 실행해 본 결과입니다. 캡쳐 이미지는 `images/` 폴더에 아래 파일 이름으로 저장하면 자동으로 표시됩니다.

- 실습 일자: (작성)
- 실행 환경: Windows PowerShell, Python (버전 작성)
- 사용 모델: claude-haiku-4-5

### 1. 전송 내용 미리 보기 (dry-run)

**명령문**

```powershell
python main.py commit --dry-run
```

**설명**

API를 호출하지 않고 AI에게 전달될 시스템 프롬프트와 사용자 프롬프트(브랜치, git status, git diff)를 확인했다. 비용 없이 입력 내용을 점검할 수 있다.

**결과 캡쳐**

![dry-run 결과](images/01-dry-run.png)

**프로그램 흐름**

`main()` 함수가 아래 순서로 함수를 호출한다. `--dry-run`이라 6번까지만 실행하고 끝난다.

| 순서 | 호출되는 함수 | 이번 실행에서 |
| --- | --- | --- |
| 1 | `parse_args()` | 실행 |
| 2 | `os.environ.get("AI_API_KEY")` | 값은 읽지만 검사는 통과 (`--dry-run`) |
| 3 | `collect_status()` → `run_git()` | 실행 |
| 4 | `collect_diff()` → `run_git()` | 실행 |
| 5 | `mask_sensitive()`, `limit_diff()` | 건너뜀 (`--safe-mode` 없음) |
| 6 | `build_user_prompt()` | 실행 |
| 7 | `print_block()` 2회 | 프롬프트를 출력하고 종료 |
| - | `call_ai()`, `polish_commit()` | 도달하지 않음 |

**1. `parse_args()` : 입력 해석**

- `argparse`로 받을 수 있는 명령과 옵션의 규칙을 등록한 뒤, 터미널에 입력한 `commit --dry-run`을 그 규칙에 맞춰 해석한다.
- 결과로 `args.command = "commit"`, `args.dry_run = True`가 만들어지고, 생략한 옵션에는 기본값(`model = claude-haiku-4-5`, `temperature = 0.2`, `max_tokens = 800`)이 들어간다.
- 해석이 끝나면 값의 범위와 조합을 추가로 검사한다. `--temperature`가 0.0~1.0을 벗어나거나, `--base`를 `commit`과 함께 쓰면 여기서 오류를 내고 끝난다.

**2. `os.environ.get("AI_API_KEY")` : API Key 확인**

- 환경변수에서 키를 읽는다. 키를 코드에 적지 않기 위한 방식이다.
- 키가 없으면 설정 방법을 안내하고 종료하지만, `--dry-run`일 때는 API를 호출하지 않으므로 키가 없어도 통과시킨다.

**3. `collect_status()` : 변경 파일 목록과 브랜치 수집 합니다**

- 내부에서 `run_git(["status", "--porcelain", "-b"])`를 호출한다.
- `run_git()`은 `subprocess.run`으로 git 명령을 실행하고, 화면에 찍힐 출력을 붙잡아 문자열로 돌려주는 공통 함수다. git이 실패하면(저장소가 아닌 폴더 등) 오류 메시지를 담아 예외를 낸다.
- 돌려받은 출력의 첫 줄(`## main...origin/main`)에서 브랜치 이름을 뽑고, 나머지 줄을 변경 파일 목록으로 쓴다.
- 이번 실행 결과: 브랜치 `main`, 변경 파일 3개.

**4. `collect_diff()` : 변경 내용 수집**

- 내부에서 `run_git(["diff", "HEAD"])`를 호출해 마지막 커밋 이후 바뀐 내용을 가져온다.
- 커밋이 하나도 없는 저장소라면 `git diff --cached`와 `git diff`를 합쳐서 쓰고, `--base`가 지정되면 `git diff <base>...HEAD`를 쓴다.
- 이번 실행 결과: 264줄. 여기까지 끝나면 `[INFO] Git status 수집 완료`, `[INFO] Git diff 수집 완료` 두 줄이 출력된다.
- 변경 파일도 없고 diff도 비어 있으면 "변경 사항이 없습니다"를 출력하고 여기서 끝난다.

**5. `mask_sensitive()`, `limit_diff()` : 민감정보 처리 (이번에는 건너뜀)**

- `--safe-mode`를 붙였을 때만 실행된다.
- `mask_sensitive()`는 정규표현식으로 API Key, 토큰, 이메일, 전화번호 형태를 찾아 `[MASKED_...]`로 바꾸고 몇 건을 바꿨는지 센다.
- `limit_diff()`는 diff를 파일 단위로 나눠 앞의 10개 파일, 200줄까지만 남긴다.

**6. `build_user_prompt()` : 프롬프트 조립**

- 3, 4번에서 모은 브랜치 이름, 변경 파일 목록, diff에 `[현재 브랜치]`, `[git status]`, `[git diff]` 제목을 붙여 하나의 글로 묶는다. 이것이 사용자 프롬프트다.
- 시스템 프롬프트는 명령에 따라 고른다. `commit`이므로 커밋 메시지의 형식과 규칙을 적어 둔 `COMMIT_SYSTEM_PROMPT`가 선택된다.

**7. `print_block()` : 프롬프트 출력 후 종료**

- `--dry-run`이므로 "API를 호출하지 않습니다. (AI API 호출 횟수: 0회)"를 출력한다.
- `print_block("System Prompt", ...)`, `print_block("User Prompt", ...)`를 차례로 호출한다. 이 함수는 `--- 제목 ---`, 내용, 구분선 순서로 출력한다.
- `return 0`으로 프로그램이 끝나고, 그 아래에 있는 `call_ai()`는 실행되지 않는다.

### 2. 커밋 메시지 생성

**명령문**

```powershell
python main.py commit
```

**설명**

git status와 git diff를 수집해 AI API를 1회 호출하고, 제목 1줄과 본문 불릿으로 된 커밋 메시지를 받았다.

- 수집 결과: 4개 파일 변경, diff 323줄
- 호출 조건: model=claude-haiku-4-5, temperature=0.2, max_tokens=800, 호출 횟수 1회
- 생성된 제목: `chore: Task8 실습 기록 및 디버그 설정 추가` (50자 이내)
- 본문: 불릿 3개에 변경 파일 3개(`.vscode/launch.json`, `README.md`, `main.py`)가 각각 언급됨

**결과 캡쳐**

![커밋 메시지 생성 결과](images/02-commit.png)

**프로그램 흐름**

6번까지는 실습 1번과 같고, `--dry-run`이 없으므로 7~9번이 이어서 실행된다.

| 순서 | 호출되는 함수 | 이번 실행에서 |
| --- | --- | --- |
| 1 | `parse_args()` | `args.command = "commit"`, 옵션은 모두 기본값 |
| 2 | `os.environ.get("AI_API_KEY")` | 키가 있어 통과 (없으면 여기서 종료) |
| 3 | `collect_status()` → `run_git()` | 브랜치 `main`, 변경 파일 4개 |
| 4 | `collect_diff()` → `run_git()` | diff 323줄 |
| 5 | `mask_sensitive()`, `limit_diff()` | 건너뜀 (`--safe-mode` 없음) |
| 6 | `build_user_prompt()` | 프롬프트 조립 |
| 7 | `call_ai()` | AI API 1회 호출 |
| 8 | `polish_commit()` → `strip_code_fence()`, `clean_title()` | 형식 검증과 후처리 |
| 9 | `print_block()` | 커밋 메시지 출력 |

1~6번의 자세한 역할은 실습 1번의 설명과 같다. 달라지는 점은 2번에서 **키가 반드시 있어야** 한다는 것이다. 아래는 새로 실행되는 7~9번이다.

**7. `call_ai()` : AI API 호출**

호출 직전에 `[INFO] AI API 요청 중... (model=..., temperature=..., max_tokens=...)`가 출력된다. 함수 안에서는 세 가지 일을 한다.

- **요청 구성**: 모델, `max_tokens`, `temperature`, 시스템 프롬프트, 사용자 프롬프트를 담은 본문(JSON)을 만든다. 헤더에는 API Key(`x-api-key`), API 버전(`anthropic-version`), 본문 형식(`content-type`)을 넣고, `https://api.anthropic.com/v1/messages`로 보낼 POST 요청을 준비한다.
- **전송과 예외 대응**: `urllib.request.urlopen`으로 보내고 최대 60초를 기다린다. 실패는 종류별로 나눠 잡는다. 서버가 오류 코드를 준 경우(`HTTPError`)는 `describe_http_error()`가 401(인증 실패), 404(모델명 오류), 429(요청 한도 초과) 등을 사람이 읽을 문장으로 바꾼다. 서버에 닿지 못한 경우(`URLError`)와 시간 초과(`TimeoutError`)도 따로 처리한다. 어느 경우든 `[ERROR] AI API 호출에 실패했습니다: 원인`을 출력하고 종료한다.
- **응답 처리**: 받은 JSON의 `content` 안에서 글자(`text`) 부분만 꺼내 돌려준다. `stop_reason`이 `max_tokens`이면 답이 중간에 잘린 것이므로 경고를 출력한다.

호출이 끝나면 `[INFO] AI API 호출 횟수: 1회`가 출력된다.

**8. `polish_commit()` : 형식 검증과 후처리**

AI가 규칙을 항상 지키는 것은 아니므로, 받은 글을 검사하고 어긴 부분을 고친다. 다시 호출하지 않고 프로그램이 직접 고치기 때문에 API 호출은 1회로 끝난다.

- `strip_code_fence()`: AI가 답을 코드 블록 기호로 감싼 경우 그 줄을 지운다.
- `clean_title()`: 첫 줄을 제목으로 보고 앞뒤의 따옴표, `#` 같은 군더더기를 뗀다. 72자를 넘으면 잘라내고 `[WARN]`으로 알린다.
- 제목이 권장 길이인 50자를 넘으면 경고를 출력한다.
- 제목과 본문 사이를 빈 줄 하나로 맞춰 최종 메시지를 만든다.

이번 실행에서는 제목이 50자 이내였고 고칠 부분이 없어 경고가 출력되지 않았다.

**9. `print_block()` : 결과 출력**

- `[DONE] 커밋 메시지 생성 완료`를 출력한다.
- `print_block("Commit Message", ...)`로 `--- Commit Message ---`, 메시지 내용, 구분선을 출력한다. 구분선은 사용자가 어디부터 어디까지 복사하면 되는지 알 수 있게 하기 위한 것이다.
- 마지막으로 "AI가 만든 초안입니다. 내용을 검토한 뒤 적용하세요."를 출력하고 종료한다.

### 3. PR 초안 생성

**명령문**

```powershell
python main.py pr
```

**설명**

git status와 git diff를 수집해 AI API를 1회 호출하고, PR 제목 1줄과 Why / What / How to Test 세 섹션으로 된 본문을 받았다.

- 수집 결과: 브랜치 `main`, 4개 파일 변경, diff 430줄
- 호출 조건: model=claude-haiku-4-5, temperature=0.2, max_tokens=800, 호출 횟수 1회
- 생성된 제목: `docs: Task8 실습 기록 및 디버그 설정 추가` (80자 이내)
- 본문: Why / What / How to Test 세 섹션이 모두 있고 각 섹션에 불릿이 1개 이상 들어 있음

**결과 캡쳐**

![PR 초안 생성 결과](images/03-pr.png)

**프로그램 흐름**

호출 순서는 실습 2번(`commit`)과 같고, `pr` 명령이라 세 곳이 달라진다. 시스템 프롬프트가 PR용으로 바뀌고, 후처리 함수가 `polish_pr()`이며, 출력이 제목과 본문 두 구획으로 나뉜다.

| 순서 | 호출되는 함수 | 이번 실행에서 |
| --- | --- | --- |
| 1 | `parse_args()` | `args.command = "pr"`, 옵션은 모두 기본값 |
| 2 | `os.environ.get("AI_API_KEY")` | 키가 있어 통과 |
| 3 | `collect_status()` → `run_git()` | 브랜치 `main`, 변경 파일 4개 |
| 4 | `collect_diff()` → `run_git()` | `--base`가 없어 `git diff HEAD` 사용, 430줄 |
| 5 | `mask_sensitive()`, `limit_diff()` | 건너뜀 (`--safe-mode` 없음) |
| 6 | `build_user_prompt()` | 프롬프트 조립, 시스템 프롬프트는 `PR_SYSTEM_PROMPT` |
| 7 | `call_ai()` | AI API 1회 호출 |
| 8 | `polish_pr()` → `strip_code_fence()`, `clean_title()` | 제목 분리, 섹션 검증과 후처리 |
| 9 | `print_block()` 2회 | PR 제목과 PR 본문을 각각 출력 |

1~5번과 7번의 역할은 실습 1, 2번의 설명과 같다. 아래는 `pr` 명령에서 달라지는 부분이다.

**3~4. 수집 결과 출력에 브랜치가 추가됨**

- `pr` 명령일 때만 `[INFO] 현재 브랜치: main`을 먼저 출력한다. PR은 브랜치 단위로 만들기 때문에 어느 브랜치의 변경인지 보여 주는 것이다.
- 브랜치 이름은 `collect_status()`가 `git status --porcelain -b` 출력의 첫 줄에서 뽑아 둔 값이다.
- `--base main`처럼 기준 브랜치를 주면 `collect_diff()`가 `git diff main...HEAD`를 실행해 두 브랜치의 차이를 가져온다. 이번에는 주지 않았으므로 커밋하지 않은 변경(`git diff HEAD`)을 썼다.

**6. `build_user_prompt()` : PR용 프롬프트 선택**

- 사용자 프롬프트(브랜치, git status, git diff)를 조립하는 방식은 `commit`과 같다.
- 시스템 프롬프트는 `PR_SYSTEM_PROMPT`가 선택된다. 첫 줄을 `TITLE: <type>: <요약>` 형식으로 쓰고, 이어서 `## Why`, `## What`, `## How to Test` 세 섹션을 반드시 넣고, 각 섹션에 불릿을 1개 이상 쓰라는 규칙이 들어 있다.
- 같은 입력이라도 이 지시문이 달라서 커밋 메시지가 아닌 PR 양식의 답이 나온다.

**8. `polish_pr()` : 제목 분리와 섹션 검증**

AI의 답 하나에서 제목과 본문을 나누고, 본문이 템플릿 규칙을 지켰는지 검사한다.

- `strip_code_fence()`로 코드 블록 기호가 있는 줄을 지운다.
- `TITLE:`로 시작하는 줄을 찾아 제목으로 삼는다. 없으면 첫 줄을 제목으로 본다.
- `clean_title()`로 제목 앞의 `TITLE:`과 따옴표를 떼고, 80자를 넘으면 잘라낸 뒤 `[WARN]`으로 알린다.
- 제목 아래의 본문을 `##` 헤더 기준으로 섹션별로 나눈다.
- Why, What, How to Test 순서로 하나씩 확인한다.
  - 섹션이 없으면 새로 추가하고 `- (작성 필요)`를 넣은 뒤 경고를 출력한다.
  - 섹션은 있는데 불릿이 없으면 각 줄 앞에 `- `를 붙여 불릿 형식으로 바꾸고 경고를 출력한다.
- 세 섹션을 정해진 순서로 다시 조립한다. AI가 추가로 쓴 다른 섹션이 있으면 뒤에 붙인다.

이번 실행에서는 제목이 80자 이내였고 세 섹션과 불릿이 모두 있어 경고가 출력되지 않았다.

**9. `print_block()` : 제목과 본문을 나눠 출력**

- `[DONE] PR 초안 생성 완료`를 출력한다.
- `print_block("PR Title", ...)`로 제목을, `print_block("PR Body", ...)`로 본문을 각각 구분선으로 감싸 출력한다. GitHub의 PR 작성 화면이 제목 칸과 본문 칸으로 나뉘어 있어, 따로 복사하기 쉽게 한 것이다.
- 마지막으로 "AI가 만든 초안입니다. 내용을 검토한 뒤 적용하세요."를 출력하고 종료한다.

### 4. 브랜치 기준 PR 초안 생성 (--base)

**명령문**

```powershell
git checkout -b task8
git add .
git commit -m "task8 branch"
python main.py pr --base main
```

**설명**

`main`에서 갈라진 작업 브랜치 `task8`을 만들어 지금까지의 작업을 커밋한 뒤, `main` 브랜치와의 차이를 기준으로 PR 초안을 만들었다. 실제로 GitHub에 PR을 올릴 때와 같은 방식이다.

- 브랜치: `feature/task8`로 만들려 했으나 예전 과제에서 만든 `feature` 브랜치가 있어 이름이 충돌했고, `task8`로 만들었다.
- 커밋 결과: `[task8 60894a6]`, 8개 파일 변경(이미지 6개 추가 포함), 417줄 추가
- 수집 결과: 현재 브랜치 `task8`, `main...HEAD` 차이 488줄
- 생성된 제목: `docs: Task8 실습 기록 및 디버그 설정 추가`
- 본문: Why 2개, What 5개, How to Test 5개 불릿으로 세 섹션이 모두 채워짐

**결과 캡쳐**

![--base 실행 결과](images/04-task8-branch.png)

**프로그램 흐름**

호출 순서는 실습 3번(`pr`)과 같다. `--base main`을 주었기 때문에 **4번 `collect_diff()`가 가져오는 diff가 달라지는 것**이 핵심이다.

| 순서 | 호출되는 함수 | 이번 실행에서 |
| --- | --- | --- |
| 1 | `parse_args()` | `args.command = "pr"`, `args.base = "main"` |
| 2 | `os.environ.get("AI_API_KEY")` | 키가 있어 통과 |
| 3 | `collect_status()` → `run_git()` | 브랜치 `task8`, 아직 커밋하지 않은 파일 1개 |
| 4 | `collect_diff()` → `run_git()` | `git diff main...HEAD` 실행, 488줄 |
| - | `--base` 차이 확인 | 차이가 있어 통과 |
| 5 | `mask_sensitive()`, `limit_diff()` | 건너뜀 (`--safe-mode` 없음) |
| 6 | `build_user_prompt()` | 프롬프트 조립, 시스템 프롬프트는 `PR_SYSTEM_PROMPT` |
| 7 | `call_ai()` | AI API 1회 호출 |
| 8 | `polish_pr()` → `strip_code_fence()`, `clean_title()` | 제목 분리, 섹션 검증과 후처리 |
| 9 | `print_block()` 2회 | PR 제목과 PR 본문을 각각 출력 |

**1. `parse_args()` : `--base` 옵션 해석과 검사**

- `--base main`이 `args.base = "main"`으로 들어간다.
- `--base`는 PR에서만 의미가 있으므로, `commit` 명령과 함께 쓰면 여기서 "`--base`는 pr 명령에서만 쓸 수 있습니다" 오류를 내고 끝난다.

**3. `collect_status()` : 브랜치 이름이 `task8`로 바뀜**

- `git status --porcelain -b`의 첫 줄이 `## task8`이 되어, `[INFO] 현재 브랜치: task8`이 출력된다.
- "1개 파일 변경 감지"는 커밋 후에도 남아 있는, 아직 커밋하지 않은 파일 수다. `--base`를 쓸 때는 이 파일의 내용이 AI에게 전달되는 diff에는 들어가지 않는다(아래 4번 참고).

**4. `collect_diff()` : 비교 기준이 브랜치로 바뀜**

`--base` 유무에 따라 실행하는 git 명령이 달라진다.

| 상황 | 실행 명령 | 가져오는 내용 |
| --- | --- | --- |
| `--base` 없음 (실습 2, 3번) | `git diff HEAD` | 마지막 커밋 이후 아직 **커밋하지 않은** 변경 |
| `--base main` (이번) | `git diff main...HEAD` | `main`에서 갈라진 뒤 `task8`에 **커밋한** 변경 전체 |

- `main...HEAD`의 점 세 개는 "두 브랜치가 갈라진 지점부터 지금 브랜치(`HEAD`)까지"를 뜻한다. 그사이 `main`에 다른 커밋이 쌓여도 그 내용은 섞이지 않고, 이 브랜치에서 한 작업만 나온다.
- PR은 "이 브랜치를 `main`에 합치면 무엇이 바뀌는가"를 설명하는 글이므로, 이 방식이 실제 PR 내용과 일치한다.

**`--base` 차이 확인 : 차이가 없으면 API를 호출하지 않음**

- `main()`에서 `args.base`가 있는데 diff가 비어 있으면 "'main' 브랜치와 현재 브랜치 사이에 커밋된 차이가 없습니다"를 출력하고 종료한다.
- `main` 브랜치에서 `--base main`을 실행하거나, 작업 브랜치를 만들고 아직 커밋하지 않은 경우가 여기에 해당한다. 내용 없이 AI를 호출해 비용을 쓰는 것을 막기 위한 검사다.
- 이번에는 커밋된 차이가 488줄 있어 통과했다.

**6~9. 이후 단계**

프롬프트 조립, AI 호출, `polish_pr()`의 섹션 검증, 출력 방식은 실습 3번과 같다. 이번에는 제목이 80자 이내였고 세 섹션에 불릿이 모두 있어 경고가 출력되지 않았다.

### 5. safe-mode 켜기/끄기 비교

**명령문**

```powershell
Add-Content test_secret.py 'API_KEY = "sk-ant-api03-AbCdEfGhIjKlMnOpQrStUvWx"'
Add-Content test_secret.py 'Tel = "010-9077-7097"'
git add test_secret.py
python main.py commit --dry-run
python main.py commit --safe-mode --dry-run
```

**설명**

가짜 API Key와 휴대폰 번호를 넣은 테스트 파일 `test_secret.py`를 만들고, `--dry-run`으로 API는 호출하지 않은 채 AI에게 **전송될 내용**을 비교했다.

| 줄 | safe-mode 끔 | safe-mode 켬 |
| --- | --- | --- |
| `API_KEY` (2줄) | `sk-ant-api03-AbCd...` 그대로 | `[MASKED_API_KEY]` |
| `Tel` | `010-9077-7097` 그대로 | `[MASKED_PHONE]` |
| `.vscode/launch.json` 변경 | 그대로 | 그대로 (민감정보 없음) |

- safe-mode를 끄면 API Key와 전화번호가 그대로 외부 AI 서버로 전송된다. 켜면 가려진 상태로 전송된다.
- 민감정보가 없는 `launch.json` 변경은 양쪽이 같다. safe-mode는 정해진 형태의 값만 바꾸고 나머지 diff는 건드리지 않는다.
- 이번 diff는 200줄보다 짧아 분량 제한(파일 10개, 200줄)으로 잘린 부분은 없다.

**결과 캡쳐**

safe-mode 끔

![safe-mode 끔](images/05.safemode-off.png)

safe-mode 켬

![safe-mode 켬](images/05.safemode-on.png)

**확인한 한계: 형식이 다르면 가려지지 않는다**

처음에는 전화번호를 `0101-9077-7097`로 잘못 입력했는데, safe-mode를 켜도 가려지지 않았다. 휴대폰 번호 패턴이 `01[016789]-?\d{3,4}-?\d{4}`, 즉 `010`처럼 **세 자리로 시작하는 번호**만 찾기 때문이다. `010-9077-7097`로 고치자 `[MASKED_PHONE]`으로 가려졌다.

정규표현식은 정해 둔 모양과 똑같은 것만 찾으므로 오타가 섞인 번호, 일반 전화(`02-123-4567`), 국제 형식(`+82-10-...`)은 놓친다. 반대로 패턴을 너무 넓히면 날짜나 버전 번호까지 가려진다. 그래서 safe-mode만 믿지 말고 `--dry-run`으로 실제 전송 내용을 확인해야 한다.

**프로그램 흐름**

두 실행 모두 `--dry-run`이라 실습 1번과 같은 순서로 진행되고, safe-mode를 켰을 때만 **5번 단계가 실행되는 것**이 차이다.

| 순서 | 호출되는 함수 | safe-mode 끔 | safe-mode 켬 |
| --- | --- | --- | --- |
| 1 | `parse_args()` | `args.safe_mode = False` | `args.safe_mode = True` |
| 2 | `os.environ.get("AI_API_KEY")` | 통과 (`--dry-run`) | 통과 (`--dry-run`) |
| 3 | `collect_status()` → `run_git()` | 같음 | 같음 |
| 4 | `collect_diff()` → `run_git()` | 같음 | 같음 |
| 5 | `mask_sensitive()` → `limit_diff()` | 건너뜀 | **실행** |
| 6 | `build_user_prompt()` | 원본 diff로 조립 | 가공된 diff로 조립 |
| 7 | `print_block()` 2회 | 출력 후 종료 | 출력 후 종료 |

3, 4번에서 수집하는 내용은 같다. safe-mode는 **수집한 뒤, AI에게 보내기 전에** diff를 가공하는 단계다.

**5-1. `mask_sensitive()` : 민감정보 가리기**

- `MASK_PATTERNS`에 등록된 정규표현식을 위에서부터 하나씩 diff 전체에 적용해, 찾은 값을 정해진 글자로 바꾼다.
- `pattern.subn()`은 바꾼 결과와 함께 몇 건을 바꿨는지 돌려주고, 이 숫자를 모두 더해 `[INFO] safe-mode 적용: 마스킹 N건`으로 출력한다.
- diff 전체에 적용하므로 새로 추가한 줄(`+`)뿐 아니라 앞뒤 문맥으로 함께 나오는 기존 줄(맨 앞이 공백인 줄)도 가려진다. 캡쳐에서 첫 번째 `API_KEY` 줄이 그 경우다.

| 패턴 | 찾는 형태 | 바뀌는 글자 |
| --- | --- | --- |
| API Key | `sk-ant-...`, `sk-...`, `AIza...`, `AKIA...`, `ghp_...` | `[MASKED_API_KEY]` 등 |
| Bearer 토큰 | `Bearer 긴문자열` | `[MASKED_TOKEN]` |
| 비밀값 | `password`, `secret`, `token`, `api_key`로 끝나는 이름에 `=` 또는 `:`로 넣은 값 | `[MASKED_SECRET]` |
| 이메일 | `아이디@도메인.com` | `[MASKED_EMAIL]` |
| 휴대폰 번호 | `010-1234-5678` 형태 | `[MASKED_PHONE]` |

- 이번 실행에서 `API_KEY` 줄은 값이 `sk-ant-`로 시작해 API Key 패턴에, `Tel` 줄은 값이 `010-`으로 시작해 휴대폰 번호 패턴에 걸렸다. `Tel`이라는 이름은 판단에 쓰이지 않는다.

**5-2. `limit_diff()` : 전송 분량 제한**

- diff를 `diff --git` 줄 기준으로 파일별로 나눠 앞의 10개 파일만 남기고, 다시 앞에서부터 200줄까지만 남긴다.
- 잘라낸 경우 diff 끝에 `[... safe-mode: 파일 N개 생략, N줄 생략]`을 붙여 AI에게도 일부가 빠졌다는 사실을 알린다.
- 이번에는 diff가 짧아 잘린 부분이 없다. 커밋하지 않은 큰 변경(예: 긴 README 수정)이 함께 있으면 그 파일이 200줄을 먼저 채워, 뒤에 있는 파일은 전송 대상에서 빠질 수 있다.

**실습 중 고친 점**

테스트 중 API Key 한 줄이 두 번 세어지는 문제를 발견했다. API Key 패턴이 값을 `[MASKED_API_KEY]`로 바꾼 뒤, 이름에 `API_KEY`가 들어 있어 비밀값 패턴이 그 결과를 다시 `[MASKED_SECRET]`으로 바꿨기 때문이다. 비밀값 패턴이 이미 `[MASKED_`로 시작하는 값은 건너뛰도록 정규표현식에 조건(`(?!\[MASKED_)`)을 추가해, 건수가 실제 개수와 같게 나오고 API Key도 `[MASKED_API_KEY]`로 정확히 표시되게 했다.

### 6. temperature 변경 비교

**명령문**

```powershell
python main.py commit --temperature 0.0
python main.py commit --temperature 1.0
```

**설명**

같은 변경 사항(10개 파일, diff 162줄)을 두고 temperature만 바꿔 실행했다. 모델과 max_tokens(800)는 같고, 두 번 모두 API를 1회 호출했다.

| 항목 | temperature 0.0 | temperature 1.0 |
| --- | --- | --- |
| 제목 | `feat: Task8 safe-mode 테스트 문서 및 이미지 업데이트` | `feat: Task8 safe-mode 문서 및 테스트 이미지 업데이트` |
| 불릿 1 | README.md에서 safe-mode 테스트 설명을 간소화하고 새 이미지 파일명으로 변경 | README.md의 safe-mode 설명을 간결하게 정리하고, 테스트 과정과 결과를 명확하게 재작성 |
| 불릿 2 | 기존 이미지(05-safe-off.png, 05-safe-on.png) 삭제 및 새 이미지(05.safemode-*.png) 추가 | 이미지 파일명을 `05-safe-*.png`에서 `05.safemode-*.png`로 변경하고 화이트 버전 추가 |
| 불릿 3 | test_secret.py에 테스트용 API Key와 전화번호 추가, launch.json에 Task8 디버그 설정 추가 | test_secret.py에 API Key와 전화번호 테스트 데이터 추가 및 디버그 구성 등록 |

관찰한 점

- **형식은 같다**: 두 결과 모두 `feat:` 제목 1줄과 불릿 3개로, 시스템 프롬프트의 규칙을 똑같이 지켰다. 형식은 temperature가 아니라 프롬프트가 정한다.
- **표현이 달라진다**: 다룬 내용(README, 이미지, test_secret.py)은 같지만, 1.0에서는 단어 순서가 바뀌고("테스트 문서" → "문서 및 테스트 이미지") "명확하게 재작성", "화이트 버전"처럼 0.0에 없던 표현이 나왔다.
- **0.0이 더 사실에 가깝다**: 0.0은 "삭제 및 추가"처럼 diff에 보이는 동작을 그대로 적었고, 1.0은 "재작성"처럼 해석이 섞인 표현을 썼다.

각각 한 번씩만 실행한 결과라 차이를 일반화하기에는 부족하다. 같은 값으로 2~3번씩 반복 실행해 보면, 0.0은 매번 거의 같은 문구가 나오고 1.0은 실행할 때마다 달라지는 것을 더 분명히 확인할 수 있다. 커밋 메시지처럼 일관성이 중요한 글에는 낮은 값이 적합해서 기본값을 0.2로 두었다.

**결과 캡쳐**

temperature 0.0

![temperature 0.0](images/06.temperature_0.0.png)

temperature 1.0

![temperature 1.0](images/06.temperature_1.0.png)

**프로그램 흐름**

호출 순서는 실습 2번(`commit`)과 같다. `--temperature` 값은 **1번에서 읽혀 7번 `call_ai()`의 요청 본문에 그대로 들어가는 것**이 전부이고, 나머지 단계에는 영향을 주지 않는다.

| 순서 | 호출되는 함수 | temperature가 하는 일 |
| --- | --- | --- |
| 1 | `parse_args()` | `--temperature 0.0` → `args.temperature = 0.0` (실수로 변환, 범위 검사) |
| 2 | `os.environ.get("AI_API_KEY")` | 영향 없음 |
| 3 | `collect_status()` → `run_git()` | 영향 없음 (두 실행 모두 10개 파일) |
| 4 | `collect_diff()` → `run_git()` | 영향 없음 (두 실행 모두 162줄) |
| 5 | `mask_sensitive()`, `limit_diff()` | 건너뜀 (`--safe-mode` 없음) |
| 6 | `build_user_prompt()` | 영향 없음 (두 실행의 프롬프트는 같다) |
| 7 | `call_ai()` | 요청 본문의 `"temperature"` 값으로 전달 |
| 8 | `polish_commit()` | 영향 없음 (받은 글을 같은 규칙으로 검사) |
| 9 | `print_block()` | 영향 없음 |

**1. `parse_args()` : 값 읽기와 검사**

- `type=float`로 등록되어 있어 터미널에서 받은 글자 `"0.0"`, `"1.0"`이 숫자로 바뀐다. `--temperature abc`처럼 숫자가 아니면 여기서 오류가 난다.
- 해석 뒤 `0.0 <= args.temperature <= 1.0`인지 검사한다. 범위를 벗어나면 "`--temperature`는 0.0~1.0 사이여야 합니다"를 출력하고 API를 호출하기 전에 끝낸다.
- 옵션을 생략하면 기본값 `DEFAULT_TEMPERATURE = 0.2`가 들어간다.

**7. `call_ai()` : 요청에 담아 전송**

- 요청 본문(`payload`)에 `"temperature": temperature`로 들어간다. 이 숫자를 실제로 해석하는 곳은 프로그램이 아니라 **AI 서버**다.
- 호출 직전에 출력되는 `[INFO] AI API 요청 중... (model=..., temperature=0.0, max_tokens=800)` 줄로 어떤 값이 전달됐는지 확인할 수 있다.
- AI는 글을 한 단어씩 이어 쓰면서 매번 다음에 올 후보 단어들 중 하나를 고른다. temperature는 이때 얼마나 과감하게 고를지를 정한다.
  - **낮을수록(0.0)**: 가장 가능성이 높은 단어를 거의 항상 고른다. 결과가 안정적이고 반복 실행해도 비슷하다.
  - **높을수록(1.0)**: 가능성이 낮은 단어도 자주 고른다. 표현이 다양해지는 대신 실행마다 결과가 달라지고, 사실과 어긋난 표현이 섞일 가능성도 커진다.

같은 입력에 같은 프롬프트를 넣었는데도 두 결과의 문구가 달라진 것은, 프로그램 안이 아니라 7번에서 서버로 넘어간 이 숫자 하나 때문이다.

### 7. max-tokens 변경 비교

**명령문**

```powershell
python main.py pr --max-tokens 50
```

**설명**

AI가 쓸 수 있는 응답 길이를 기본값 800 토큰에서 50 토큰으로 줄여 PR 초안을 만들었다. 토큰은 AI가 글을 세는 단위로, 한국어는 대략 한 글자에서 몇 글자가 1토큰이 된다.

- 수집 결과: 브랜치 `task8`, 14개 파일 변경, diff 232줄
- 호출 조건: model=claude-haiku-4-5, temperature=0.2, **max_tokens=50**, 호출 횟수 1회

관찰한 점

| 단계 | 출력 | 의미 |
| --- | --- | --- |
| AI 응답 직후 | `[WARN] max_tokens에 도달해 응답이 잘렸을 수 있습니다.` | AI가 글을 다 쓰기 전에 50토큰 한도에서 멈췄다 |
| 후처리 | `[WARN] PR 본문에 'What' 섹션이 없어 추가했습니다.` | Why를 쓰는 도중에 끊겨 What이 없었다 |
| 후처리 | `[WARN] PR 본문에 'How to Test' 섹션이 없어 추가했습니다.` | How to Test도 없었다 |
| 최종 결과 | Why 불릿이 `safe-mode 기능의 테스트 결과를`에서 끊김 | 문장이 중간에 잘린 채 남았다 |
| 최종 결과 | What, How to Test에 `- (작성 필요)` | 프로그램이 빈 섹션을 채워 템플릿 형식만 맞췄다 |

- 제목(`docs: Task8 safe-mode 테스트 문서 및 이미지 업데이트`)은 응답 맨 앞에 있어 온전히 받았다.
- 프로그램이 멈추거나 오류가 나지 않고, 잘린 결과를 받아 경고와 함께 Why / What / How to Test 구조는 지켜서 출력했다.
- 다만 내용은 쓸 수 없는 수준이다. max_tokens는 비용(출력 토큰)과 응답 시간을 줄여 주지만, 너무 작으면 결과 자체가 망가진다. PR 본문처럼 섹션이 여러 개인 글은 충분한 값이 필요해 기본값을 800으로 두었다.

**결과 캡쳐**

![max-tokens 50 결과](images/07.max-token.png)

**프로그램 흐름**

호출 순서는 실습 3번(`pr`)과 같다. max_tokens가 작아서 **7번 `call_ai()`에서 경고가 나고, 8번 `polish_pr()`에서 빠진 섹션을 채우는 분기가 실제로 실행된 것**이 차이다. 지금까지의 실습에서 후처리 경고가 처음으로 나온 경우다.

| 순서 | 호출되는 함수 | 이번 실행에서 |
| --- | --- | --- |
| 1 | `parse_args()` | `args.max_tokens = 50` (정수로 변환, 1 이상인지 검사) |
| 2 | `os.environ.get("AI_API_KEY")` | 키가 있어 통과 |
| 3 | `collect_status()` → `run_git()` | 브랜치 `task8`, 14개 파일 |
| 4 | `collect_diff()` → `run_git()` | 232줄 |
| 5 | `mask_sensitive()`, `limit_diff()` | 건너뜀 (`--safe-mode` 없음) |
| 6 | `build_user_prompt()` | 프롬프트 조립 (max_tokens와 무관) |
| 7 | `call_ai()` | 요청에 `max_tokens: 50` 전달, 응답의 `stop_reason`이 `max_tokens` → **경고 출력** |
| 8 | `polish_pr()` → `strip_code_fence()`, `clean_title()` | What, How to Test가 없어 **섹션 추가 + 경고 2개** |
| 9 | `print_block()` 2회 | 보정된 PR 제목과 본문 출력 |

**1. `parse_args()` : 값 읽기와 검사**

- `type=int`로 등록되어 있어 `"50"`이 정수 50으로 바뀐다. `--max-tokens 50.5`나 `abc`처럼 정수가 아니면 여기서 오류가 난다.
- 해석 뒤 `args.max_tokens < 1`인지 검사해 0이나 음수를 막는다.

**7. `call_ai()` : 한도 전달과 잘림 감지**

- 요청 본문에 `"max_tokens": 50`으로 들어간다. temperature와 마찬가지로 이 숫자를 적용하는 곳은 **AI 서버**다. 서버는 50토큰을 쓰면 문장 중간이라도 멈춘다.
- 서버는 응답과 함께 멈춘 이유(`stop_reason`)를 알려 준다. 정상적으로 다 썼으면 `end_turn`, 한도에 걸려 멈췄으면 `max_tokens`다.
- 코드는 이 값을 확인해 `max_tokens`이면 경고를 출력한다. 화면의 첫 번째 `[WARN]`이 여기서 나왔다.

```python
if data.get("stop_reason") == "max_tokens":
    warn("max_tokens에 도달해 응답이 잘렸을 수 있습니다. --max-tokens 값을 늘려 보세요.")
```

- 잘렸어도 오류로 처리하지 않고, 받은 만큼의 글을 다음 단계로 넘긴다. 비용을 이미 쓴 응답을 버리지 않기 위해서다.

**8. `polish_pr()` : 빠진 섹션 채우기**

AI가 받은 글은 `TITLE:` 줄과 `## Why` 아래 불릿 하나가 중간에서 끊긴 상태였다. `polish_pr()`이 이를 검사한 순서는 다음과 같다.

1. `TITLE:` 줄을 찾아 제목으로 분리한다. 제목은 온전했고 80자 이내라 그대로 쓴다.
2. 본문을 `##` 헤더 기준으로 나눈다. `Why` 섹션 하나만 나온다.
3. Why, What, How to Test 순서로 확인한다.
   - **Why**: 섹션이 있고 `- `로 시작하는 불릿이 있어 그대로 둔다. 문장이 끊긴 것은 형식 검사로는 알 수 없어 그대로 남는다.
   - **What**: 섹션이 없어 `- (작성 필요)`를 넣어 추가하고 경고를 출력한다.
   - **How to Test**: 같은 방법으로 추가하고 경고를 출력한다.
4. 세 섹션을 정해진 순서로 다시 조립한다.

이 후처리 덕분에 출력은 항상 과제의 PR 템플릿 규칙(세 섹션 헤더 + 섹션별 불릿 1개 이상)을 만족한다. 하지만 `(작성 필요)`라는 표시와 경고로 **사람이 직접 채워야 할 곳을 알려 줄 뿐, 내용을 만들어 내지는 않는다.** 이럴 때는 `--max-tokens` 값을 늘려 다시 실행하는 것이 맞는 대응이다.

### 8. 오류 상황: API Key 미설정

**명령문**

```powershell
Remove-Item Env:AI_API_KEY
python main.py commit
```

첫 줄은 현재 PowerShell 창에 설정된 `AI_API_KEY`를 지우는 명령이다. 새 PowerShell 창을 열어 키를 설정하지 않은 상태로 실행해도 같은 결과가 나온다.

**설명**

API Key 환경변수가 없는 상태에서 `commit`을 실행했다.

- `[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.`로 원인을 알려 준다.
- 바로 아래에 설정 방법을 두 가지(macOS/Linux의 `export`, Windows PowerShell의 `$env:`) 보여 준다. 사용자가 이 줄을 복사해 키만 바꿔 넣으면 된다.
- `[INFO] Git status 수집 완료` 같은 줄이 하나도 없다. Git 수집이나 AI 호출 전에, 프로그램의 거의 첫 단계에서 멈췄다는 뜻이다.
- AI API를 호출하지 않았으므로 비용이 들지 않는다.
- 종료 코드 1로 끝나 "실패"를 알린다. 정상 종료(0)와 구분되므로, 다른 스크립트에서 이 프로그램을 부를 때 실패 여부를 판단할 수 있다.

키를 코드에 적지 않고 환경변수로만 읽는다는 과제 요구사항과, 키가 없을 때 원인을 알려 준다는 예외 처리 요구사항을 함께 확인한 실습이다.

**결과 캡쳐**

![API Key 미설정](images/08.API%20Key%20미설정.png)

**프로그램 흐름**

`main()`이 함수 두 개만 거치고 끝난다. 이후 단계는 모두 실행되지 않는다.

| 순서 | 호출되는 함수 | 이번 실행에서 |
| --- | --- | --- |
| 1 | `parse_args()` | `args.command = "commit"`, `args.dry_run = False` |
| 2 | `os.environ.get("AI_API_KEY")` | 빈 값 → **오류 출력 후 종료 (코드 1)** |
| - | `collect_status()` 이후 전부 | 도달하지 않음 |

**1. `parse_args()` : 입력 해석**

- 명령과 옵션을 정상적으로 해석한다. 이 단계는 키와 무관해서 통과한다.

**2. 키 확인 : 오류 처리와 종료**

```python
api_key = os.environ.get(API_KEY_ENV, "").strip()
if not api_key and not args.dry_run:
    error(f"{API_KEY_ENV} 환경변수가 설정되지 않았습니다.")
    print(f'## 예) export {API_KEY_ENV}="YOUR_KEY"')
    print(f'## 예) (PowerShell) $env:{API_KEY_ENV}="YOUR_KEY"')
    return 1
```

- `os.environ.get(API_KEY_ENV, "")`: 환경변수 `AI_API_KEY`를 읽는다. 없으면 오류를 내지 않고 두 번째 값인 빈 문자열 `""`을 돌려준다.
- `.strip()`: 앞뒤 공백을 지운다. 실수로 공백만 넣은 경우도 "없음"으로 처리하기 위해서다.
- `if not api_key and not args.dry_run`: 키가 비어 있고, **동시에** `--dry-run`이 아닐 때만 막는다. `--dry-run`은 API를 호출하지 않으므로 키가 없어도 실행할 수 있게 둔 것이다.
- `error(...)`: 앞에 `[ERROR]`를 붙여 출력하는 함수다. 화면의 첫 줄이 여기서 나온다.
- `print(...)` 두 줄: 설정 방법 예시를 출력한다. 문구 안의 `{API_KEY_ENV}` 자리에 실제 변수 이름 `AI_API_KEY`가 들어간다.
- `return 1`: `main()`을 여기서 끝낸다. 파일 맨 아래의 `sys.exit(main())`이 이 값을 받아 종료 코드 1로 프로그램을 끝낸다.

**왜 이 위치에서 검사하나**

키 검사를 Git 수집보다 먼저 하는 것은, 어차피 AI를 호출할 수 없는 상황에서 git 명령을 실행하고 diff를 모으는 일을 하지 않기 위해서다. 실패할 것이 확실한 조건은 가능한 한 앞에서 확인하고 끝내는 것이 사용자에게도 빠르고, 불필요한 작업도 줄인다.

종료 코드는 PowerShell에서 실행 직후 `$LASTEXITCODE`를 입력하면 확인할 수 있다.

### 9. 오류 상황: 잘못된 API Key

**명령문**

```powershell
Add-Content test_9.txt "bad key test"
$realKey = $env:AI_API_KEY
$env:AI_API_KEY="wrong-key"
python main.py commit
$env:AI_API_KEY = $realKey
Remove-Item test_9.txt
```

- 1행: 변경이 없으면 AI 호출 전에 종료되므로, 호출 단계까지 가도록 임시 파일을 하나 만들었다.
- 2행: 진짜 키를 `$realKey`에 잠시 보관했다.
- 3~4행: 틀린 키를 넣고 실행했다.
- 5~6행: 실습 후 진짜 키로 되돌리고 임시 파일을 지웠다.

**설명**

형식만 갖춘 틀린 키(`wrong-key`)로 `commit`을 실행했다.

- `[INFO] Git status 수집 완료: 1개 파일 변경 감지`: 임시 파일 `test_9.txt`가 새 파일(`??`)로 잡혔다.
- `[INFO] Git diff 수집 완료: 0줄`: 새 파일은 아직 `git add`하지 않아 `git diff HEAD`에는 나오지 않는다. 그래도 변경 파일이 1개 있어 종료하지 않고 다음 단계로 진행했다.
- `[INFO] AI API 요청 중...`: 실제로 서버에 요청을 보냈다.
- `[ERROR] AI API 호출에 실패했습니다: HTTP 401 인증 실패(API Key를 확인하세요): invalid x-api-key`

마지막 오류 줄은 세 부분으로 되어 있다.

| 부분 | 내용 | 만든 곳 |
| --- | --- | --- |
| `HTTP 401` | 서버가 돌려준 상태 코드 | 서버 |
| `인증 실패(API Key를 확인하세요)` | 상태 코드를 사람이 읽을 말로 바꾸고 할 일을 안내 | 프로그램 (`describe_http_error`) |
| `invalid x-api-key` | 서버가 응답 본문에 담아 보낸 원인 설명 | 서버 |

서버의 원래 메시지만 보여 주면 영어 문구만 남고, 프로그램이 정한 문구만 보여 주면 서버가 알려 준 구체적인 원인이 빠진다. 둘을 함께 보여 줘서 "무엇이 잘못됐고 무엇을 하면 되는지"를 한 줄로 알 수 있게 했다.

- `AI API 호출 횟수: 1회` 줄은 나오지 않는다. 이 줄은 호출이 **성공했을 때만** 출력된다.
- 프로그램이 예외로 멈추지 않고(Traceback 없음) 정리된 메시지를 낸 뒤 종료 코드 1로 끝났다.
- 인증에 실패한 요청은 비용이 청구되지 않는다.

**결과 캡쳐**

![잘못된 API Key](images/09-bad-key.png)

**프로그램 흐름**

8번(키 없음)은 Git 수집 전에 멈췄지만, 9번은 키가 "있기는 하므로" AI 호출까지 진행한 뒤 서버의 거절을 받고 멈춘다. 키가 맞는지는 서버에 보내 봐야 알 수 있기 때문이다.

| 순서 | 호출되는 함수 | 이번 실행에서 |
| --- | --- | --- |
| 1 | `parse_args()` | `args.command = "commit"` |
| 2 | `os.environ.get("AI_API_KEY")` | `"wrong-key"`가 있어 통과 |
| 3 | `collect_status()` → `run_git()` | 변경 파일 1개 (`?? test_9.txt`) |
| 4 | `collect_diff()` → `run_git()` | 0줄 |
| - | 변경 유무 확인 | 변경 파일이 있어 통과 |
| 5 | `mask_sensitive()`, `limit_diff()` | 건너뜀 (`--safe-mode` 없음) |
| 6 | `build_user_prompt()` | 프롬프트 조립 (diff 자리에는 "새로 추가된 미추적 파일만 있음" 안내) |
| 7 | `call_ai()` → `describe_http_error()` | 서버가 401 반환 → **오류 출력 후 종료 (코드 1)** |
| - | `polish_commit()`, `print_block()` | 도달하지 않음 |

8번과 비교

| | 8번 (키 없음) | 9번 (틀린 키) |
| --- | --- | --- |
| 멈추는 곳 | 2. 키 확인 | 7. `call_ai()` |
| `[INFO] Git ... 수집 완료` 줄 | 없음 | 있음 |
| 서버에 요청 | 보내지 않음 | 보냈고 서버가 거절 |
| 원인을 판단한 곳 | 프로그램 | 서버 |

**6. `build_user_prompt()` : diff가 비었을 때**

- diff가 0줄이면 `[git diff]` 자리에 "(diff 없음: 새로 추가된 미추적 파일만 있음)"을 넣는다. AI가 빈칸을 보고 엉뚱한 추측을 하지 않도록, 왜 비었는지 알려 주는 것이다.

**7. `call_ai()` : HTTP 오류 처리**

요청을 보내는 부분은 정상일 때와 같다. 서버가 401로 답하면 `urllib`이 `HTTPError` 예외를 일으키고, 아래 코드가 이를 잡는다.

```python
except urllib.error.HTTPError as exc:
    raise ApiError(describe_http_error(exc))
```

`describe_http_error()`는 두 가지를 꺼내 한 문장으로 만든다.

```python
detail = json.loads(exc.read().decode("utf-8"))["error"]["message"]   # 서버 설명: "invalid x-api-key"
reasons = {401: "인증 실패(API Key를 확인하세요)", 404: ..., 429: ...}
return f"HTTP {exc.code} {reason}: {detail}"
```

- `exc.code`: 상태 코드 401
- `exc.read()`: 서버가 보낸 응답 본문(JSON). 그 안의 `error.message`가 `invalid x-api-key`다. 본문을 읽지 못하면 대신 짧은 기본 설명을 쓴다.
- `reasons`: 자주 나오는 상태 코드마다 사람이 할 일을 적어 둔 표다. 목록에 없는 코드는 500번대면 "서버 오류", 그 외는 "요청 실패"로 표시한다.

이렇게 만든 문장은 `ApiError`라는 이 프로그램 전용 예외에 담겨 `main()`으로 올라가고, `main()`이 받아서 출력하고 끝낸다.

```python
except ApiError as exc:
    error(f"AI API 호출에 실패했습니다: {exc}")
    return 1
```

예외를 이렇게 한 단계씩 넘기는 이유는 역할을 나누기 위해서다. `call_ai()`는 "무엇이 실패했는지"만 정리하고, 화면 출력과 종료는 `main()`이 한곳에서 맡는다. 네트워크 오류(`URLError`)와 시간 초과(`TimeoutError`)도 같은 길로 올라와 같은 형식의 `[ERROR]` 줄로 출력된다.

### 10. 변경 사항이 없는 경우

**명령문**

```powershell
git status
python main.py commit
```

**설명**

모든 변경을 커밋해 `git status`가 `nothing to commit, working tree clean`인 상태에서 실행했다.

- `[INFO] 변경 사항이 없습니다. 커밋 메시지를 생성하지 않고 종료합니다.`를 출력하고 끝난다.
- `[INFO] AI API 요청 중...` 줄이 없다. 바꾼 내용이 없는데 AI를 호출하면 쓸모없는 결과에 비용만 들기 때문에, 호출 전에 멈춘다.
- 오류가 아니라 "할 일이 없음"이므로 종료 코드는 0(정상)이다. 8번(API Key 미설정)이 1로 끝나는 것과 다르다.

준비 과정에서 확인한 점

- `git status`는 Task8 폴더만이 아니라 **Codyssey26 저장소 전체**를 본다. Task8 밖에 있는 `.vscode/launch.json`이 수정된 채 남아 있으면 변경으로 잡히므로, 이것까지 커밋해야 했다.
- 새로 만들고 아직 `git add`하지 않은 파일(`??`)도 변경으로 센다. 그래서 테스트 파일(`test_secret.py`, `test_tel`)을 지우고, 흰 배경 원본 이미지(`*-white.png`)는 `.gitignore`에 넣어 Git이 무시하게 했다.
- 프로그램은 API Key를 Git보다 먼저 검사하므로, 키가 없으면 이 메시지 대신 8번의 키 오류가 먼저 나온다. 키를 설정한 상태에서 실행해야 한다.

**결과 캡쳐**

![변경 사항 없음](images/10.no-change.png)

**프로그램 흐름**

`main()`이 Git 수집까지 마친 뒤, 변경 유무 확인에서 종료한다. 8번보다 한 단계 더 진행하고, AI 호출 전에 멈춘다.

| 순서 | 호출되는 함수 | 이번 실행에서 |
| --- | --- | --- |
| 1 | `parse_args()` | `args.command = "commit"` |
| 2 | `os.environ.get("AI_API_KEY")` | 키가 있어 통과 |
| 3 | `collect_status()` → `run_git()` | 브랜치 `task8`, 변경 파일 0개 |
| 4 | `collect_diff()` → `run_git()` | diff 빈 문자열 |
| - | 변경 유무 확인 | 둘 다 비어 있음 → **안내 출력 후 종료 (코드 0)** |
| - | `mask_sensitive()` 이후 전부 | 도달하지 않음 |

**3. `collect_status()` : 변경 파일 0개**

- `git status --porcelain -b`의 출력이 브랜치 줄(`## task8...origin/task8` 등) 한 줄뿐이다.
- 첫 줄은 브랜치 정보로 쓰고, 나머지 줄을 변경 파일 목록(`status_lines`)으로 쓰는데, 나머지가 없으므로 빈 리스트 `[]`가 된다.

**4. `collect_diff()` : diff 없음**

- 커밋이 있는 저장소이므로 `git diff HEAD`를 실행한다. 마지막 커밋과 지금 파일이 똑같아 출력이 빈 문자열 `""`이다.

**변경 유무 확인 : 안내 후 종료**

```python
target = "커밋 메시지를" if args.command == "commit" else "PR 초안을"
if args.base and not diff.strip():
    ...
if not status_lines and not diff.strip():
    info(f"변경 사항이 없습니다. {target} 생성하지 않고 종료합니다.")
    return 0
```

- `target`: 명령에 따라 안내 문구를 바꾼다. `pr`로 실행하면 "PR 초안을 생성하지 않고"로 나온다.
- 첫 번째 `if`는 `--base`를 썼을 때만 보는 조건이라 이번에는 건너뛴다.
- 두 번째 `if`: 변경 파일 목록이 비어 있고(`not status_lines`), **그리고** diff도 비어 있을 때(`not diff.strip()`) 종료한다. `.strip()`으로 공백과 줄바꿈만 있는 경우도 빈 것으로 본다.
- 두 조건을 모두 보는 이유: 새로 만든 파일만 있고 아직 `git add`하지 않은 경우, `git diff HEAD`에는 아무것도 안 나오지만 `git status`에는 `??`로 잡힌다. 이때는 변경이 있는 것이므로 종료하지 않고 진행해야 한다.
- `return 0`: 정상 종료다. `[INFO]`로 안내하는 것도 오류가 아니라 정보이기 때문이다.

### 11. GitHub에 push 및 PR 작성

**명령문**

```powershell
git push -u origin task8
```

**설명**

작업 브랜치를 push하고, 4번에서 생성한 PR 제목과 본문을 붙여넣어 GitHub에서 PR을 만들었다.

- PR 링크: (작성)
- AI 초안에서 고친 부분: (작성)

**결과 캡쳐**

![GitHub PR 화면](images/11-github-pr.png)
