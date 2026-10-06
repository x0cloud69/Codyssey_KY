# AI 기반 Git 커밋/PR 자동 생성기

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
