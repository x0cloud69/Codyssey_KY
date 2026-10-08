"""AI 기반 Git 커밋/PR 자동 생성기.

git status / git diff 결과를 수집해 AI API(Anthropic Messages API)에 넘기고,
커밋 메시지 또는 PR 초안을 터미널에 출력한다.

사용 예:
    python main.py commit
    python main.py pr --safe-mode
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
API_KEY_ENV = "AI_API_KEY"

DEFAULT_MODEL = "claude-haiku-4-5"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 800
REQUEST_TIMEOUT = 60

# 출력 형식 규칙
COMMIT_TITLE_RECOMMENDED = 50
COMMIT_TITLE_MAX = 72
PR_TITLE_MAX = 80
PR_SECTIONS = ["Why", "What", "How to Test"]

# safe-mode 정책
SAFE_MAX_FILES = 10
SAFE_MAX_LINES = 200
MASK_PATTERNS = [
    (re.compile(r"sk-ant-[A-Za-z0-9_\-]{10,}"), "[MASKED_API_KEY]"),
    (re.compile(r"sk-[A-Za-z0-9_\-]{20,}"), "[MASKED_API_KEY]"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{35}"), "[MASKED_API_KEY]"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[MASKED_AWS_KEY]"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"), "[MASKED_GITHUB_TOKEN]"),
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._\-]{20,}"), r"\1[MASKED_TOKEN]"),
    (
        re.compile(
            r"(?i)((?:api[_-]?key|secret|token|passwd|password)\w*\s*[:=]\s*)"
            r"(['\"]?)(?!\[MASKED_)[^\s'\"]{6,}\2"
        ),
        r"\1\2[MASKED_SECRET]\2",
    ),
    (re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"), "[MASKED_EMAIL]"),
    (re.compile(r"\b01[016789]-?\d{3,4}-?\d{4}\b"), "[MASKED_PHONE]"),
]

COMMIT_SYSTEM_PROMPT = """너는 Git 커밋 메시지를 작성하는 시니어 개발자다.
주어진 git status와 git diff만 근거로 커밋 메시지를 한국어로 작성한다.

[형식]
1행: <type>: <요약>  (type은 feat, fix, docs, refactor, test, chore, style 중 하나)
2행: 빈 줄
3행부터: 핵심 변경 사항을 '- '로 시작하는 불릿 1~3개

[규칙]
- 제목은 50자 이내, 마침표 없이 작성한다.
- 본문 불릿에는 변경된 파일(또는 모듈) 이름을 1~3개 언급한다.
- diff에 없는 내용은 추측해서 쓰지 않는다.
- 커밋 메시지 본문만 출력한다. 설명, 인사말, 코드 블록(```)은 쓰지 않는다."""

PR_SYSTEM_PROMPT = """너는 Pull Request 설명을 작성하는 시니어 개발자다.
주어진 브랜치 이름, git status, git diff만 근거로 PR 초안을 한국어로 작성한다.

[형식] 아래 구조를 그대로 지킨다.
TITLE: <type>: <요약>

## Why
- <변경 배경>

## What
- <핵심 변경 사항>

## How to Test
- <테스트 방법>

[규칙]
- TITLE은 한 줄, 80자 이내로 작성한다.
- 세 섹션 헤더(## Why, ## What, ## How to Test)는 반드시 포함하고, 각 섹션에 '- ' 불릿을 1개 이상 쓴다.
- How to Test에는 실제로 실행할 수 있는 명령이나 확인 절차를 쓴다.
- diff에 없는 내용은 추측해서 쓰지 않는다.
- 위 형식 외의 설명, 인사말, 코드 블록(```)은 쓰지 않는다."""


class GitError(Exception):
    pass


class ApiError(Exception):
    pass


def info(message):
    print(f"[INFO] {message}")


def warn(message):
    print(f"[WARN] {message}")


def error(message):
    print(f"[ERROR] {message}")


# ---------------------------------------------------------------- Git 수집

def run_git(args):
    """git 명령을 실행하고, 출력 결과를 문자열로 돌려준다.

    사람이 터미널에 git 명령을 치고 눈으로 읽는 일을 프로그램이 대신한다.
    예) run_git(["status", "--porcelain", "-b"])        -> 터미널의 `git -c core.quotepath=false status --porcelain -b` 와 같다.
    """
    try:
        # subprocess.run: 다른 프로그램을 실행하고 끝날 때까지 기다린다.
        result = subprocess.run(
            # 실행할 명령을 단어별로 나눈 리스트.
            # - 한 문자열이 아니라 리스트로 넘기면 각 조각이 글자 그대로 전달되어,
            #   값에 공백/특수문자가 있어도 다른 명령이 끼어들 수 없다(안전).
            # - "-c 설정이름=값": git 설정을 저장하지 않고 이번 실행에만 적용한다.
            #   (git config 로 저장하면 사용자 PC 설정이 영구히 바뀌므로 쓰지 않는다)
            # - core.quotepath: 한글 등 비영어 파일명을 숫자 코드로 바꿀지 정한다.
            #     true (기본값) -> 바꾼다        "\353\263\270\352\263\274\354\240\225/Task8/README.md"
            #     false         -> 바꾸지 않는다  본과정/Task8/README.md
            #   "변환 기능을 끈다"는 뜻이라, 한글을 그대로 보려면 false 로 준다.
            # - *args: 넘겨받은 리스트를 풀어서 끼워 넣는다.
            #   ["status", "-b"] -> "git", "-c", "...", "status", "-b"
            ["git", "-c", "core.quotepath=false", *args],
            # 출력을 화면에 찍지 않고 붙잡아서 result에 담는다.
            capture_output=True,
            # git이 내보낸 바이트를 UTF-8 문자열로 해석한다.
            # (지정하지 않으면 Windows에서는 cp949로 읽어 한글이 깨질 수 있다)
            encoding="utf-8",
            # 해석할 수 없는 바이트는 오류 대신 대체 문자로 바꾸고 계속 진행한다.
            errors="replace",
        )
    except FileNotFoundError:
        # git 프로그램 자체가 설치되어 있지 않은 경우
        raise GitError("git 명령을 찾을 수 없습니다. Git 설치 여부를 확인하세요.")
    # result에 담기는 것
    # - result.returncode: 종료 코드 (0이면 성공, 그 외는 실패)
    # - result.stdout    : 정상 출력 글자
    # - result.stderr    : 오류 메시지 (예: "fatal: not a git repository")
    if result.returncode != 0:
        raise GitError(result.stderr.strip() or "git 명령 실행에 실패했습니다.")
    return result.stdout


def collect_status():
    """git status 결과에서 (브랜치 이름, 커밋 존재 여부, 변경 파일 줄 목록)을 얻는다."""
    # --porcelain: 사람이 아니라 "프로그램"이 읽기 쉬운 고정 형식으로 출력한다.
    #   일반 git status 는 긴 안내 문장이고 버전/언어에 따라 문구가 바뀌지만,
    #   --porcelain 은 항상 한 줄에 "상태코드 파일경로" 하나씩이라 줄 단위로 해석할 수 있다.
    #   상태코드 예)  " M" 수정(add 전)   "M " 수정(add 후)   "A " 새 파일 add
    #                 "D " 삭제           "??" Git이 아직 모르는 새 파일
    # -b (--branch): 첫 줄에 브랜치 정보를 추가한다. ("## main...origin/main")
    #
    # 두 옵션의 역할 구분
    #   --porcelain               -> 출력 "형식"(전체 틀)을 고정된 모양으로
    #   -c core.quotepath=false   -> 그 안의 "한글 파일 이름"을 숫자 코드로 바꾸지 않고 그대로
    lines = run_git(["status", "--porcelain", "-b"]).splitlines()
    header = lines[0][3:] if lines and lines[0].startswith("## ") else ""
    has_commits = not header.startswith("No commits yet on ")
    branch = header.replace("No commits yet on ", "").split("...")[0].strip()
    return branch or "(알 수 없음)", has_commits, lines[1:]


def collect_diff(has_commits, base=None):
    if base:
        return run_git(["diff", f"{base}...HEAD"])
    if has_commits:
        return run_git(["diff", "HEAD"])
    return run_git(["diff", "--cached"]) + run_git(["diff"])


# ---------------------------------------------------------------- safe-mode

def mask_sensitive(text):
    count = 0
    for pattern, replacement in MASK_PATTERNS:
        text, replaced = pattern.subn(replacement, text)
        count += replaced
    return text, count


def limit_diff(diff, max_files=SAFE_MAX_FILES, max_lines=SAFE_MAX_LINES):
    """diff를 파일 max_files개, 총 max_lines줄까지만 남긴다."""
    chunks = re.split(r"(?m)^(?=diff --git )", diff)
    chunks = [chunk for chunk in chunks if chunk.strip()]
    notes = []
    if len(chunks) > max_files:
        notes.append(f"파일 {len(chunks) - max_files}개 생략")
        chunks = chunks[:max_files]
    lines = "".join(chunks).splitlines()
    if len(lines) > max_lines:
        notes.append(f"{len(lines) - max_lines}줄 생략")
        lines = lines[:max_lines]
    limited = "\n".join(lines)
    if notes:
        limited += f"\n[... safe-mode: {', '.join(notes)}]"
    return limited, notes


# ---------------------------------------------------------------- AI API

def call_ai(api_key, system_prompt, user_prompt, model, temperature, max_tokens):
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": API_VERSION,
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise ApiError(describe_http_error(exc))
    except urllib.error.URLError as exc:
        raise ApiError(f"네트워크 오류: {exc.reason}")
    except TimeoutError:
        raise ApiError(f"응답 시간 초과({REQUEST_TIMEOUT}초)")
    except json.JSONDecodeError:
        raise ApiError("응답을 JSON으로 해석할 수 없습니다.")

    text = "".join(
        block.get("text", "")
        for block in data.get("content", [])
        if block.get("type") == "text"
    ).strip()
    if not text:
        raise ApiError("응답에 텍스트가 없습니다.")
    if data.get("stop_reason") == "max_tokens":
        warn("max_tokens에 도달해 응답이 잘렸을 수 있습니다. --max-tokens 값을 늘려 보세요.")
    return text


def describe_http_error(exc):
    try:
        detail = json.loads(exc.read().decode("utf-8"))["error"]["message"]
    except Exception:
        detail = exc.reason
    reasons = {
        400: "잘못된 요청",
        401: "인증 실패(API Key를 확인하세요)",
        403: "권한 없음",
        404: "모델 또는 주소를 찾을 수 없음(--model 값을 확인하세요)",
        429: "요청 한도 초과(잠시 후 다시 시도하세요)",
        529: "서버 과부하(잠시 후 다시 시도하세요)",
    }
    reason = reasons.get(exc.code, "서버 오류" if exc.code >= 500 else "요청 실패")
    return f"HTTP {exc.code} {reason}: {detail}"


# ---------------------------------------------------------------- 검증/후처리

def strip_code_fence(text):
    lines = [line for line in text.strip().splitlines() if not line.startswith("```")]
    return "\n".join(lines).strip()


def clean_title(title, max_length, label):
    title = re.sub(r"^(TITLE:|#+)\s*", "", title.strip()).strip("\"'` ")
    if len(title) > max_length:
        warn(f"{label}이 {len(title)}자라 {max_length}자로 줄였습니다.")
        title = title[: max_length - 1].rstrip() + "…"
    return title


def polish_commit(text):
    lines = strip_code_fence(text).splitlines()
    title = clean_title(lines[0] if lines else "", COMMIT_TITLE_MAX, "커밋 제목")
    if len(title) > COMMIT_TITLE_RECOMMENDED:
        warn(f"커밋 제목이 {len(title)}자입니다(권장 {COMMIT_TITLE_RECOMMENDED}자 이내).")
    body = "\n".join(lines[1:]).strip()
    return f"{title}\n\n{body}" if body else title


def polish_pr(text):
    lines = strip_code_fence(text).splitlines()
    title_index = next(
        (i for i, line in enumerate(lines) if line.strip().upper().startswith("TITLE:")),
        0,
    )
    title = clean_title(lines[title_index] if lines else "", PR_TITLE_MAX, "PR 제목")
    body = "\n".join(lines[title_index + 1 :])

    # '## 헤더' 기준으로 섹션을 나눈다.
    sections = {}
    current = None
    for line in body.splitlines():
        header = re.match(r"^#{1,6}\s*(.+?)\s*$", line)
        if header:
            current = header.group(1)
            sections.setdefault(current, [])
        elif current is not None and line.strip():
            sections[current].append(line.rstrip())

    def find_section(name):
        for key in sections:
            if key.lower().startswith(name.lower()):
                return sections.pop(key)
        return None

    output = []
    for name in PR_SECTIONS:
        content = find_section(name)
        if content is None:
            warn(f"PR 본문에 '{name}' 섹션이 없어 추가했습니다. 직접 채워 주세요.")
            content = []
        if not any(re.match(r"^\s*[-*] ", line) for line in content):
            if content:
                warn(f"'{name}' 섹션에 불릿이 없어 불릿 형식으로 바꿨습니다.")
                content = [f"- {line.strip()}" for line in content]
            else:
                content = ["- (작성 필요)"]
        output.append(f"## {name}\n" + "\n".join(content))
    for name, content in sections.items():
        output.append(f"## {name}\n" + "\n".join(content))
    return title, "\n\n".join(output)


# ---------------------------------------------------------------- 출력

def print_block(header, content):
    line = f"--- {header} ---"
    print(line)
    print(content)
    print("-" * len(line))


# ---------------------------------------------------------------- 실행 흐름

def build_user_prompt(branch, status_lines, diff):
    status_text = "\n".join(status_lines) or "(없음)"
    diff_text = diff.strip() or "(diff 없음: 새로 추가된 미추적 파일만 있음)"
    return (
        f"[현재 브랜치]\n{branch}\n\n"
        f"[git status]\n{status_text}\n\n"
        f"[git diff]\n{diff_text}"
    )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="git status/diff를 바탕으로 커밋 메시지와 PR 초안을 생성합니다."
    )
    parser.add_argument("command", choices=["commit", "pr"], help="생성할 대상")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"모델 (기본값: {DEFAULT_MODEL})")
    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"0.0~1.0, 낮을수록 일관된 결과 (기본값: {DEFAULT_TEMPERATURE})",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=f"응답 최대 토큰 수 (기본값: {DEFAULT_MAX_TOKENS})",
    )
    parser.add_argument(
        "--safe-mode",
        action="store_true",
        help=f"민감정보 마스킹 + diff 제한(파일 {SAFE_MAX_FILES}개, {SAFE_MAX_LINES}줄)",
    )
    parser.add_argument(
        "--base",
        help="(pr 전용) 비교 기준 브랜치. 지정하면 git diff <base>...HEAD 를 사용",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="API를 호출하지 않고 전송될 프롬프트만 출력",
    )
    args = parser.parse_args(argv)
    if not 0.0 <= args.temperature <= 1.0:
        parser.error("--temperature는 0.0~1.0 사이여야 합니다.")
    if args.max_tokens < 1:
        parser.error("--max-tokens는 1 이상이어야 합니다.")
    if args.base and args.command != "pr":
        parser.error("--base는 pr 명령에서만 쓸 수 있습니다.")
    return args


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    args = parse_args(argv)

    api_key = os.environ.get(API_KEY_ENV, "").strip()
    if not api_key and not args.dry_run:
        error(f"{API_KEY_ENV} 환경변수가 설정되지 않았습니다.")
        print(f'## 예) export {API_KEY_ENV}="YOUR_KEY"')
        print(f'## 예) (PowerShell) $env:{API_KEY_ENV}="YOUR_KEY"')
        return 1

    try:
        branch, has_commits, status_lines = collect_status()
        diff = collect_diff(has_commits, args.base)
    except GitError as exc:
        error(f"Git 정보를 수집하지 못했습니다: {exc}")
        print("## Git이 초기화된 프로젝트 루트 디렉토리에서 실행했는지 확인하세요.")
        return 1

    target = "커밋 메시지를" if args.command == "commit" else "PR 초안을"
    if args.base and not diff.strip():
        info(f"'{args.base}' 브랜치와 현재 브랜치({branch}) 사이에 커밋된 차이가 없습니다. PR 초안을 생성하지 않고 종료합니다.")
        print("## 작업 브랜치에서 변경을 커밋한 뒤 다시 실행하세요.")
        return 0
    if not status_lines and not diff.strip():
        info(f"변경 사항이 없습니다. {target} 생성하지 않고 종료합니다.")
        return 0

    if args.command == "pr":
        info(f"현재 브랜치: {branch}")
    info(f"Git status 수집 완료: {len(status_lines)}개 파일 변경 감지")
    info(f"Git diff 수집 완료: {len(diff.splitlines())}줄")

    if args.safe_mode:
        diff, masked = mask_sensitive(diff)
        diff, notes = limit_diff(diff)
        summary = f"마스킹 {masked}건"
        if notes:
            summary += ", " + ", ".join(notes)
        info(f"safe-mode 적용: {summary}")

    system_prompt = COMMIT_SYSTEM_PROMPT if args.command == "commit" else PR_SYSTEM_PROMPT
    user_prompt = build_user_prompt(branch, status_lines, diff)

    if args.dry_run:
        info("dry-run: API를 호출하지 않습니다. (AI API 호출 횟수: 0회)")
        print_block("System Prompt", system_prompt)
        print_block("User Prompt", user_prompt)
        return 0

    info(
        f"AI API 요청 중... (model={args.model}, "
        f"temperature={args.temperature}, max_tokens={args.max_tokens})"
    )
    try:
        answer = call_ai(
            api_key, system_prompt, user_prompt,
            args.model, args.temperature, args.max_tokens,
        )
    except ApiError as exc:
        error(f"AI API 호출에 실패했습니다: {exc}")
        return 1
    info("AI API 호출 횟수: 1회")

    if args.command == "commit":
        message = polish_commit(answer)
        print("[DONE] 커밋 메시지 생성 완료\n")
        print_block("Commit Message", message)
    else:
        title, body = polish_pr(answer)
        print("[DONE] PR 초안 생성 완료\n")
        print_block("PR Title", title)
        print()
        print_block("PR Body", body)
    print("\n※ AI가 만든 초안입니다. 내용을 검토한 뒤 적용하세요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
