# Task6 과제 목표 6가지 — 설명 대본

> 문제.txt **「3. 과제 목표」**의 6개 항목에 대한 답변 정리입니다.
> 각 항목은 **① 30초 대본(그대로 말하면 되는 문장)** → **② 풀어서 설명** → **③ 내 코드 근거** → **④ 꼬리질문 대비** 순서입니다.
> 폭넓은 예상 질문은 `QnA.md`, 코드를 처음부터 읽는 방법은 `GUIDE-HTML-CSS.md`를 참고하세요.

---

## 목표 1. 시맨틱 태그를 왜 쓰는가, 어떤 기준으로 구조를 설계했는가

### ① 30초 대본

> "`div`는 의미가 없는 상자지만 `header`, `nav`, `main` 같은 시맨틱 태그는 **그 영역의 역할을 태그 자체로 표현**합니다.
> 화면에 보이는 모습은 같지만, 스크린리더가 영역 단위로 건너뛸 수 있고 검색엔진이 중요한 내용을 파악할 수 있습니다.
> 저는 **'화면에서 하는 역할'을 기준**으로 구조를 나눴습니다. 이동 링크 묶음은 `nav`, 제목을 가진 주제 덩어리는 `section`,
> 떼어내도 혼자 의미가 통하는 프로젝트 카드는 `article`을 썼습니다."

### ② 풀어서 설명

**왜 쓰는가 — 3가지**

| 이유 | 설명 |
| --- | --- |
| 접근성 | 스크린리더가 "탐색 메뉴", "본문"으로 구분해 읽고, 사용자가 원하는 영역으로 건너뜀 |
| 검색엔진(SEO) | 검색 로봇이 `main` 안을 핵심 내용으로, `footer`를 부가 정보로 판단 |
| 유지보수 | `</div></div></div>` 대신 `</section></main>` → 코드 읽기가 쉬움 |

**구조 설계 기준 — 역할별로 태그 선택**

| 태그 | 쓴 곳 | 고른 이유 |
| --- | --- | --- |
| `<header>` | 로고 + 메뉴 | 페이지 맨 위에 반복되는 머리 영역 |
| `<nav>` | 메뉴 링크 목록 | 다른 곳으로 **이동**하는 링크 묶음 |
| `<main>` | Hero ~ Contact | 페이지의 **핵심 내용** (페이지당 1개) |
| `<section>` | 6개 섹션 | **제목(h2)을 가진 주제 덩어리** |
| `<article>` | 프로젝트 카드 | **떼어내도 혼자 의미가 통함** |
| `<footer>` | 저작권 · 소셜 | 바닥글 |
| `<ul><li>` | 메뉴, Skills | 순서 없는 **목록** |
| `<dl><dt><dd>` | About 정보 | "항목 : 값" 형태의 **설명 목록** |

추가로 지킨 것:

- 제목은 `h1`(Hero, 1개) → `h2`(섹션) → `h3`(카드) 순서로 **건너뛰지 않음**
- 모든 이미지에 **의미 있는 `alt`** (장식용 이모지는 `aria-hidden="true"`)
- 폼은 `label for` = `input id` 로 연결, 에러 메시지는 `aria-describedby`로 연결
- `div`는 **레이아웃을 묶는 용도로만** 사용 (`.container`, `.about-inner` 등)

### ③ 내 코드 근거

- `index.html` 전체 — `header` / `nav` / `main` / `section` / `footer`
- `main.js` 241줄 `createProjectCard()` — 동적으로 만드는 카드도 `<article>`

### ④ 꼬리질문

**Q. `section`과 `article`의 차이는?**
> `article`은 따로 떼어내도 완전한 내용, `section`은 큰 글 안의 한 주제 묶음입니다. 프로젝트 카드는 카드 하나만 공유해도 의미가 통해서 `article`을 썼습니다.

**Q. `div`를 아예 안 쓰는 게 좋은가요?**
> 아닙니다. 의미를 붙일 게 없고 순전히 레이아웃을 위해 묶을 때는 `div`가 맞습니다. 의미가 있는데도 `div`를 쓰는 것이 문제입니다.

**Q. 시맨틱 태그를 쓰면 화면이 달라지나요?**
> 거의 같습니다. `section`이나 `div`나 기본 스타일은 사실상 동일합니다. 차이는 **기계가 이해하는 의미**입니다.

---

## 목표 2. Flexbox와 Grid의 차이, 언제 각각을 선택하는가

### ① 30초 대본

> "**Flexbox는 한 줄(1차원)**, **Grid는 행과 열(2차원)** 배치에 강합니다.
> 요소들을 **한 방향으로 나란히** 놓을 때는 Flex를, **여러 줄의 칸을 맞춰야** 할 때는 Grid를 씁니다.
> 저는 네비게이션처럼 로고와 메뉴를 한 줄에 양 끝으로 배치하는 곳에 Flex를 썼고,
> 프로젝트 카드처럼 가로세로 줄을 맞춰야 하는 목록에 Grid를 썼습니다."

### ② 풀어서 설명

| | Flexbox | Grid |
| --- | --- | --- |
| 방향 | 가로 **또는** 세로 한 방향 | 가로 **와** 세로 동시에 |
| 기준 | **내용물** 크기에 맞춰 배치 | **틀(칸)**을 먼저 정하고 배치 |
| 잘 맞는 곳 | 메뉴 바, 버튼 묶음, 정렬 | 카드 목록, 갤러리, 페이지 틀 |

**내 선택 기준**

| 위치 | 선택 | 이유 |
| --- | --- | --- |
| `.nav` | Flex | 로고 ↔ 메뉴를 한 줄 양 끝으로 (`justify-content: space-between`) |
| Hero 버튼 · 필터 버튼 · 푸터 | Flex | 한 줄 나열 + `flex-wrap`으로 자동 줄바꿈 |
| About (이미지 + 글) | Flex | 모바일 `column` → 태블릿 `row`, **방향만 바꾸면 됨** |
| `.projects-grid` | Grid | 카드들의 **가로세로 줄을 맞춰야** 함 |
| `.skills-list` | Grid | 2칸 → 3칸으로 **칸 수만** 바꾸면 됨 |

**Grid의 핵심 한 줄**

```css
grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
```

"한 칸은 최소 280px, 남는 공간은 똑같이 나누고, 칸 수는 자동" →
**미디어 쿼리 없이** 모바일 1열 → 태블릿 2열 → 데스크톱 3열이 됩니다.

### ③ 내 코드 근거

- `style.css` 6번 섹션 `.nav` — Flex
- `style.css` 10번 섹션 `.projects-grid` (513줄) — Grid + auto-fit
- `style.css` 9번 섹션 `.skills-list` — Grid

### ④ 꼬리질문

**Q. `auto-fit`과 `auto-fill`의 차이는?**
> 카드가 적을 때 차이가 납니다. `auto-fill`은 빈 칸을 남겨두고, `auto-fit`은 빈 칸을 접어서 **있는 카드를 늘립니다.**

**Q. 둘을 같이 쓸 수 있나요?**
> 네. 제 코드에서도 Grid 안의 카드 내부는 Flex(`flex-direction: column`)로 배치했습니다. 바깥은 Grid, 안은 Flex 조합이 흔합니다.

**Q. Grid만 써도 되지 않나요?**
> 가능하지만 한 줄 배치에는 Flex가 더 짧고 직관적입니다. 메뉴 정렬에 Grid를 쓰면 칸을 일일이 정의해야 합니다.

---

## 목표 3. querySelector로 선택하고 addEventListener로 연결하는 흐름

### ① 30초 대본

> "① `querySelector`로 DOM에서 요소를 **찾아 변수에 담고**,
> ② `addEventListener`로 **'이 이벤트가 생기면 이 함수를 실행해줘'라고 예약**하고,
> ③ 사용자가 실제로 클릭하면 그 함수가 실행되어 **DOM을 바꿉니다.**
> 저는 JS에서 주로 **클래스만 붙였다 뗐다** 하고, 실제 모양 변화는 CSS가 담당하게 했습니다."

### ② 풀어서 설명

```js
// ① 찾기 — DOM에서 id로 검색해 손잡이를 변수에 담음
const hamburger = document.querySelector('#hamburger');
const navMenu = document.querySelector('#nav-menu');

// ② 예약 — "click이 발생하면 toggleMenu를 실행해줘"
hamburger.addEventListener('click', toggleMenu);

// ③ 실행 — 이벤트가 실제로 발생했을 때
const toggleMenu = () => {
  const isOpen = navMenu.classList.toggle('active');   // DOM 변경
  hamburger.setAttribute('aria-expanded', isOpen);
};
```

**중요한 감각 — DOM은 이미 만들어져 있다**

```
① index.html 을 브라우저가 읽음  →  DOM(요소 지도) 완성
② main.js 실행 (defer)           →  완성된 DOM을 찾아서 고침
```

JS는 DOM을 **만드는** 게 아니라 **주무릅니다.** (카드처럼 없던 요소를 추가할 때만 예외)

**선택자 두 가지**

| | 반환 | 쓴 곳 |
| --- | --- | --- |
| `querySelector('#id')` | 첫 번째 요소 1개 | 버튼, 폼, 상자 |
| `querySelectorAll('a[href^="#"]')` | 맞는 요소 전부 (NodeList) | 앵커 링크 전체에 이벤트 등록 |

**DOM을 바꾸는 방법 3가지 (이게 전부)**

| 방법 | 용도 | 쓴 곳 |
| --- | --- | --- |
| `classList.add/remove/toggle` | 클래스 붙였다 떼기 | 햄버거, 헤더, 스크롤탑, 애니메이션 |
| `textContent` | 글자 바꾸기 | 에러 · 성공 메시지, 테마 아이콘, 연도 |
| `innerHTML` | HTML 덩어리 교체 | 프로젝트 카드, 필터 버튼, 상태 박스 |

### ③ 내 코드 근거

- `main.js` 41~46줄 — `querySelector` 모음
- `main.js` 129줄 `hamburger.addEventListener('click', toggleMenu)`
- `style.css` `.nav-menu.active` — 실제 모양 변화는 CSS가 담당

### ④ 꼬리질문

**Q. 왜 HTML에 `onclick`을 안 쓰나요?**
> HTML(구조)과 JS(동작)를 분리하기 위해서입니다. `addEventListener`는 한 요소에 여러 이벤트를 붙일 수 있고, `{ passive: true }` 같은 옵션도 줄 수 있습니다.

**Q. `defer`는 왜 붙였나요?**
> HTML을 끝까지 읽은 뒤 JS를 실행해서, `querySelector`가 아직 없는 요소를 찾아 `null`이 되는 문제를 막기 위해서입니다.

**Q. 동적으로 만든 버튼에는 어떻게 이벤트를 붙였나요?**
> 이벤트 위임을 썼습니다. 필터 버튼은 다시 그릴 때마다 새로 만들어지므로, **항상 존재하는 부모**(`filterBar`)에 한 번만 리스너를 붙이고 `event.target.closest('.filter-btn')`로 클릭 대상을 판별했습니다. (`main.js` 389줄)

---

## 목표 4. 화살표 함수 · 구조분해 할당 · 배열 메서드가 왜 필요한가

### ① 30초 대본

> "전부 **반복을 줄이고 의도를 드러내기 위한 문법**입니다.
> 화살표 함수는 콜백을 짧게 쓰기 위해, 구조분해 할당은 객체에서 **필요한 값만 꺼내기** 위해,
> `map`은 **배열을 다른 배열로 변환**하기 위해, `filter`는 **조건에 맞는 것만 남기기** 위해 씁니다.
> 저는 GitHub 데이터를 `map`으로 카드 HTML로 바꾸고, `filter`로 언어별 필터를 구현했습니다."

### ② 풀어서 설명

**화살표 함수 `() => {}`**
- 왜 : 짧고, 이벤트 콜백을 넘길 때 읽기 쉬움
- 한 줄이면 `{}`와 `return` 생략 가능

```js
const formatDate = (isoString) => new Date(isoString).toLocaleDateString('ko-KR');
```

**템플릿 리터럴 `` `${}` ``**
- 왜 : 문자열 `+` 없이 **완성될 HTML 모양 그대로** 작성 가능

**구조분해 할당**
- 왜 : `projectState.status`처럼 매번 앞을 반복하지 않아도 됨

```js
const { status, repos, filter } = projectState;                   // 객체에서
const { scrollY } = window;
entries.forEach(({ isIntersecting, target }) => { ... });          // 매개변수에서 바로
Object.entries(fields).forEach(([fieldName, input]) => { ... });   // 배열에서
```

**`map` — 같은 개수의 다른 배열로 변환**

```js
// ① GitHub 원본(80개 항목) → 쓸 값 7개만 담은 객체 (357줄)
const repos = data.map(({ name, html_url, stargazers_count }) => ({
  name, url: html_url, stars: stargazers_count,
}));

// ② 객체 배열 → 카드 HTML 문자열 배열 → join으로 합침 (330줄)
projectsGrid.innerHTML = visibleRepos.map(createProjectCard).join('');
```

**`filter` — 조건에 맞는 것만 남기기**

```js
// 언어 필터 (322줄)
repos.filter(({ language }) => language === filter);

// 언어 목록에서 null 제거
repos.map(({ language }) => language).filter(Boolean);
```

**`forEach` — 돌면서 일 시키기 (결과 없음)**

```js
anchorLinks.forEach((link) => link.addEventListener('click', ...));
```

**그 외**
- 스프레드 `{ ...projectState, ...changes }` — 기존 상태 복사 + 변경분 덮어쓰기
- `new Set([...])` — 언어 목록 중복 제거
- `every` — 폼 3칸이 **모두** 통과했는지 확인

### ③ 내 코드 근거

- `main.js` 357줄 — `map` + 구조분해로 값 추출
- `main.js` 330줄 — `map` + `join`으로 카드 생성
- `main.js` 322줄 — `filter`로 언어별 필터링

### ④ 꼬리질문

**Q. `map`과 `forEach` 차이는?**
> `map`은 **새 배열을 반환**하고, `forEach`는 아무것도 반환하지 않습니다(undefined). 결과가 필요하면 `map`입니다.

**Q. `for`문으로도 되는데 왜 배열 메서드를 쓰나요?**
> 의도가 이름에 드러나기 때문입니다. `map`을 보면 "변환하는구나", `filter`를 보면 "거르는구나"를 바로 알 수 있고, 인덱스 변수 실수도 줄어듭니다.

**Q. `.join('')`은 왜 필요한가요?**
> `map`의 결과는 배열인데 `innerHTML`은 문자열만 받기 때문입니다. `join('')`으로 사이에 아무것도 넣지 않고 하나로 붙입니다.

---

## 목표 5. fetch와 async/await, 그리고 로딩 / 성공 / 실패 상태 표현

### ① 30초 대본

> "`async` 함수 안에서 `await fetch()`로 **응답을 기다리고**, `await response.json()`으로 데이터를 받습니다.
> 서버 응답은 시간이 걸리고 실패할 수도 있기 때문에, **status라는 하나의 값**으로
> 로딩 · 성공 · 에러 · 빈 상태를 관리하고 각 상태마다 다른 화면을 그렸습니다.
> 특히 에러 화면에는 **재시도 버튼**을 넣어 사용자에게 다음 행동을 제공했습니다."

### ② 풀어서 설명

```js
const fetchRepos = async () => {
  setProjectState({ status: 'loading' });            // ① 요청 전에 로딩 상태로
  try {
    const response = await fetch(endpoint);           // ② 응답 대기
    if (!response.ok) throw new Error(reason);        // ③ 404/403도 에러로 승격
    const data = await response.json();               // ④ JSON → JS 배열
    const repos = data.map(...);                      // ⑤ 필요한 값만 추출
    setProjectState({
      status: repos.length === 0 ? 'empty' : 'success',
      repos,
    });
  } catch (error) {
    setProjectState({ status: 'error', errorMessage: error.message });
  }
};
```

**4가지 상태와 화면**

| status | 언제 | 화면 |
| --- | --- | --- |
| `'loading'` | 요청 직후 | 스피너 + "로딩 중..." |
| `'success'` | 1개 이상 도착 | 필터 버튼 + 카드 목록 |
| `'empty'` | 0개 도착 | "표시할 프로젝트가 없습니다" |
| `'error'` | 네트워크 실패, 404, 403 | "불러올 수 없습니다" + 원인 + **다시 시도** 버튼 |

**왜 상태를 하나의 값으로 관리했나**
`isLoading`, `isError` 같은 변수로 나누면 "로딩 중인데 에러도 true"라는 **모순 상태**가 생길 수 있습니다. 하나의 `status`는 항상 네 값 중 하나만 갖습니다.

**왜 성공만 처리하면 안 되나**
느린 네트워크 · 실패 · 0개, 이 셋 모두 화면이 **똑같이 빈 화면**이 됩니다. 사용자는 원인을 알 수 없고 할 수 있는 일도 없습니다.

### ③ 내 코드 근거

- `main.js` 337줄 `fetchRepos()` — async/await + try/catch
- `main.js` 278줄 `createStatusBox()` — 상태별 화면
- `main.js` 396줄 — 재시도 버튼 (이벤트 위임)

### ④ 꼬리질문

**Q. `response.ok`는 왜 확인하나요?**
> `fetch`는 404나 403 같은 실패 응답이 와도 에러를 던지지 않습니다. 네트워크 자체가 실패했을 때만 `catch`로 갑니다. 그래서 직접 확인해 `throw`로 승격시켰습니다.

**Q. 403은 왜 따로 처리했나요?**
> GitHub API는 로그인 없이 **시간당 60회** 제한이 있어서, 한도 초과 시 "잠시 후 다시 시도해주세요"라는 안내가 더 도움이 되기 때문입니다.

**Q. 로딩 상태를 어떻게 테스트했나요?**
> 개발자도구 Network 탭에서 **Slow 3G**로 속도를 낮춰 확인했고, 에러는 **Offline**으로 전환해 확인한 뒤 다시 Online으로 바꿔 재시도 버튼을 테스트했습니다.

**Q. async/await 대신 `.then()`을 써도 되나요?**
> 동작은 같습니다. `async/await`가 위에서 아래로 읽혀 이해하기 쉽고, `try/catch`로 에러 처리를 한곳에 모을 수 있어 선택했습니다.

---

## 목표 6. 이벤트 → 상태 변경 → DOM 업데이트의 연결 (React의 기초)

### ① 30초 대본

> "제 코드의 모든 기능은 **하나의 흐름**을 따릅니다.
> 이벤트 핸들러는 **상태 변수만 바꾸고**, 화면은 **render 함수가 상태를 보고** 그립니다.
> 이렇게 하면 화면을 바꾸는 코드가 한 곳에만 있어서, 화면이 이상할 때 **상태 값만 확인하면** 원인을 찾을 수 있습니다.
> React의 `useState`는 이 흐름에서 **render 호출까지 자동으로** 해주는 것으로 이해했습니다."

### ② 풀어서 설명

```
[사용자 행동]  →  [상태 변경 함수]     →  [상태 변수]           →  [render 함수]        →  [화면]
 토글 클릭      →  setTheme()         →  theme = 'dark'       →  renderTheme()       →  전체 색 변경
 페이지 로드    →  setProjectState()  →  status = 'loading'   →  renderProjects()    →  스피너
 필터 클릭      →  setProjectState()  →  filter = 'Python'    →  renderProjects()    →  카드 1개만
 폼 입력/제출   →  validateField()    →  formErrors.email=... →  renderFieldError()  →  에러 문구
```

**연결 고리 — `main.js` 220줄**

```js
const setProjectState = (changes) => {
  projectState = { ...projectState, ...changes };   // ① 상태 갱신
  renderProjects();                                  // ② 화면 다시 그리기
};
```

상태를 바꾸는 **모든 경로(첫 로드 · 재시도 · 필터)**가 이 함수를 지나므로, 화면 갱신을 빼먹을 수 없습니다.

**필터 클릭을 예로 따라가면**

1. "Python" 버튼 **클릭** (이벤트)
2. `setProjectState({ filter: 'Python' })` → `projectState.filter` **변경** (상태)
3. `setProjectState` 내부에서 `renderProjects()` 자동 호출
4. `repos.filter(...)`로 Python만 골라 **카드 다시 그림** (DOM)

**왜 상태를 거치는가**
이벤트마다 DOM을 직접 바꾸면, 화면을 건드리는 코드가 여기저기 흩어져 서로 어긋납니다. 상태를 거치면 **화면을 그리는 곳이 한 곳**이라 추적이 쉽습니다.

**React와의 대응**

| 내 코드 | React |
| --- | --- |
| `let theme` + `setTheme()` | `const [theme, setTheme] = useState()` |
| `setProjectState` 안에서 `renderProjects()` **직접 호출** | `setState` 하면 **자동으로** 다시 그림 |
| `createProjectCard()`가 HTML 문자열 반환 | 컴포넌트가 JSX 반환 |
| `innerHTML` 통째로 교체 | 바뀐 부분만 비교해 교체 (Virtual DOM) |
| `escapeHTML()` 직접 작성 | 기본으로 자동 이스케이프 |

### ③ 내 코드 근거 — 상태 4개

| 상태 변수 | 위치 | 렌더 함수 |
| --- | --- | --- |
| `theme` | `main.js` 81줄 | `renderTheme()` (84줄) |
| `projectState` | 211줄 | `renderProjects()` (304줄) |
| `projectState.filter` | 211줄 | `renderProjects()` |
| `formErrors` | 440줄 | `renderFieldError()` (443줄) |

### ④ 꼬리질문

**Q. JS가 직접 색을 바꾸지 않는다는 게 무슨 뜻인가요?**
> JS는 `classList.toggle('active')`처럼 **클래스만** 바꾸고, 실제 색·위치 변화는 CSS의 `.nav-menu.active` 규칙이 담당합니다. 역할을 분리하면 디자인 변경 시 CSS만 고치면 됩니다.

**Q. 매번 `innerHTML`로 전부 다시 그리면 비효율적이지 않나요?**
> 맞습니다. 카드 하나만 바뀌어도 전부 새로 만듭니다. 카드 수가 적어 문제는 없지만, 규모가 커지면 React의 Virtual DOM처럼 **바뀐 부분만 교체**하는 방식이 필요합니다. 이 한계를 체감한 것이 이번 과제의 수확입니다.

**Q. 상태를 객체 하나로 묶은 이유는?**
> `status`, `repos`, `filter`가 항상 함께 화면에 반영되어야 하기 때문입니다. 스프레드로 변경분만 덮어쓰면 나머지 값은 그대로 유지됩니다.

---

## 부록. 3분 발표용 요약

> "순수 HTML·CSS·JS로 반응형 포트폴리오를 만들었습니다.
>
> **HTML**은 역할 기준으로 시맨틱 태그를 골랐고, 프로젝트 카드는 떼어내도 의미가 통해 `article`을 썼습니다.
>
> **CSS**는 모바일 퍼스트로 작성하고 768px·1024px 두 지점에서만 구조를 바꿨습니다. 한 줄 배치는 Flex, 카드 목록은 Grid를 썼고, `auto-fit`과 `minmax` 덕분에 미디어 쿼리 없이도 열 수가 자동으로 바뀝니다.
>
> **JS**는 모든 기능을 '이벤트 → 상태 변경 → 렌더' 한 가지 흐름으로 통일했습니다. 상태는 테마·프로젝트·필터·폼 네 가지이고, 각각 전용 렌더 함수가 화면을 그립니다.
>
> **API 연동**에서는 로딩·성공·에러·빈 상태를 하나의 `status` 값으로 관리해 네 가지 화면을 만들었고, 에러에는 재시도 버튼을 넣었습니다.
>
> 이 과정에서 `innerHTML`로 전부 다시 그리는 방식의 한계를 체감했고, React의 Virtual DOM이 무엇을 해결하는지 이해하게 됐습니다."
