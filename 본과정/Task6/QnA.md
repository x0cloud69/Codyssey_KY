# Task6 평가 Q&A 대비 정리

> **읽는 법**
> 각 질문마다 ① **한 줄 답** (먼저 이것부터 말하기) → ② **풀어서 설명** → ③ **내 코드 어디?** 순서로 정리했습니다.
> "내 코드 어디?"를 알고 있으면, 평가자가 "코드로 보여주세요" 할 때 바로 열어서 보여줄 수 있습니다.

<br />

## 0. 30초 전체 요약 (첫 질문 "무엇을 만들었나요?"에 대한 답)

> "순수 HTML, CSS, JavaScript로 반응형 포트폴리오를 만들었습니다.
> HTML은 **구조**, CSS는 **디자인**, JS는 **동작**으로 파일을 나눴고,
> JS는 모든 기능을 **'이벤트 → 상태 변경 → 화면 업데이트'** 한 가지 흐름으로 작성했습니다.
> 예를 들어 다크 모드 버튼을 누르면 `theme` 상태가 바뀌고, `renderTheme()`이 화면을 다시 그립니다.
> GitHub API로 저장소를 불러올 때는 로딩 · 성공 · 에러 · 빈 상태를 나눠서 각각 다른 화면을 보여줍니다."

### 파일 역할

| 파일 | 역할 | 비유 |
| --- | --- | --- |
| `index.html` | 무엇이 있는지 (구조) | 집의 뼈대 |
| `css/style.css` | 어떻게 보이는지 (디자인) | 인테리어 |
| `js/main.js` | 어떻게 움직이는지 (동작) | 전기 · 스위치 |

### `main.js` 목차 (평가 중 코드 찾을 때 사용)

| 번호 | 섹션 | 핵심 함수 / 변수 |
| --- | --- | --- |
| 0 | 설정값 | `CONFIG` (60px, 300px, 0.2) |
| 1 | DOM 선택 | `querySelector` 모음 |
| 2 | 다크 모드 | `theme`, `setTheme()`, `renderTheme()` |
| 3 | 햄버거 메뉴 | `toggleMenu()`, `closeMenu()` |
| 4 | 부드러운 스크롤 | `anchorLinks.forEach`, `scrollIntoView` |
| 5 | 스크롤 이벤트 | `handleScroll()` |
| 6 | 스크롤 애니메이션 | `revealObserver`, `observeReveal()` |
| 7 | GitHub API | `projectState`, `fetchRepos()`, `renderProjects()` |
| 8 | 폼 검사 | `validators`, `formErrors`, `validateField()`, `renderFieldError()` |
| 9 | 기타 | 푸터 연도 |

<br />

---

## 1. HTML — 시맨틱 태그

### Q1. 시맨틱 태그를 왜 사용했나요?

**한 줄 답** : 태그 이름만 보고도 "이 영역이 무슨 역할인지" 사람과 기계가 모두 알 수 있게 하려고요.

**풀어서 설명**
- `div`는 "그냥 상자"라서 의미가 없습니다. `nav`는 "메뉴", `footer`는 "바닥글"이라는 **뜻**이 있습니다.
- 좋은 점 3가지
  1. **접근성** : 스크린리더가 "탐색 메뉴", "본문" 단위로 건너뛸 수 있음
  2. **검색엔진(SEO)** : 검색 로봇이 중요한 내용(`main`, `h1`)을 잘 파악
  3. **가독성 · 유지보수** : `</div></div></div>` 대신 `</section>`이라 코드 읽기가 쉬움

**내 코드 어디?** `index.html` 전체

### Q2. 어떤 기준으로 구조를 설계했나요?

**한 줄 답** : "화면에서 하는 역할" 기준으로 나눴습니다.

| 태그 | 내가 쓴 곳 | 선택 이유 |
| --- | --- | --- |
| `<header>` | 로고 + 메뉴 | 모든 페이지 맨 위에 반복되는 머리 영역 |
| `<nav>` | 메뉴 링크 목록 | 다른 곳으로 **이동**하는 링크 묶음 |
| `<main>` | Hero ~ Contact | 이 페이지의 **핵심 내용** (페이지에 1개만) |
| `<section>` | Hero, About, Skills, Projects, Contact | **제목(h2)을 가진 주제 덩어리** |
| `<article>` | Projects 카드 1개 | 그 카드만 떼어서 다른 곳에 가져가도 **혼자 의미가 통함** |
| `<footer>` | 저작권, 소셜 링크 | 바닥글 |
| `<ul><li>` | 메뉴, Skills | 순서 없는 **목록** |
| `<dl><dt><dd>` | About 정보 (이름: KY) | "항목 : 값" 형태의 **설명 목록** |

- 제목은 `h1`(Hero, 페이지당 1개) → `h2`(섹션 제목) → `h3`(카드 제목) 순서로 건너뛰지 않았습니다.

### Q3. `section`과 `article`의 차이는?

**한 줄 답** : `article`은 **따로 떼어내도 완전한 내용**, `section`은 **큰 글 안의 한 주제 묶음**입니다.

- 프로젝트 카드는 카드 하나만 공유해도 의미가 통하므로 `article`
- About, Skills는 페이지 안의 한 부분이므로 `section`

### Q4. `alt` 속성은 어떻게 작성했나요?

**한 줄 답** : "이미지" 같은 의미 없는 말 대신, **이미지가 안 보여도 내용이 전달되게** 썼습니다.

- 예 : `alt="노트북 앞에서 웃고 있는 개발자 KY의 프로필 일러스트"`
- 스크린리더가 읽어주고, 이미지가 깨졌을 때 대신 표시됩니다.
- 장식용 이모지 아이콘은 `aria-hidden="true"`로 스크린리더가 읽지 않게 했습니다.

### Q5. `label`의 `for`와 `input`의 `id`는 왜 맞춰야 하나요?

**한 줄 답** : 둘을 **연결**해서, 라벨을 눌러도 입력칸에 커서가 가고 스크린리더가 "이름, 입력칸"이라고 읽게 하려고요.

```html
<label for="email">이메일</label>
<input type="email" id="email" />
```

- 추가로 `aria-describedby="email-error"`로 에러 메시지까지 연결해서, 에러도 함께 읽히게 했습니다.

### Q6. 폼에 `novalidate`는 왜 붙였나요?

**한 줄 답** : 브라우저 기본 말풍선 대신, **입력칸 바로 아래에 내가 만든 에러 메시지**를 보여주기 위해서입니다.

- 브라우저마다 말풍선 모양 · 문구가 달라서 통일된 UX를 만들기 어렵습니다.

<br />

---

## 2. CSS — Flexbox vs Grid, 반응형

### Q7. Flexbox와 Grid의 차이는?

**한 줄 답** : **Flexbox는 한 줄(1차원)**, **Grid는 가로 · 세로 표(2차원)** 배치에 강합니다.

| | Flexbox | Grid |
| --- | --- | --- |
| 방향 | 가로 **또는** 세로 한 방향 | 가로 **와** 세로 동시에 |
| 기준 | **내용물** 크기에 맞춰 배치 | **틀(칸)**을 먼저 정하고 배치 |
| 잘 맞는 곳 | 메뉴 바, 버튼 묶음, 가운데 정렬 | 카드 목록, 갤러리, 전체 페이지 틀 |

### Q8. 언제 각각을 선택했나요?

**한 줄 답** : 요소들을 **한 줄로 나란히** 놓을 땐 Flex, **바둑판처럼** 여러 줄로 칸을 맞출 땐 Grid를 썼습니다.

| 위치 | 선택 | 이유 |
| --- | --- | --- |
| 네비게이션 `.nav` | **Flex** | 로고 ↔ 메뉴를 한 줄에 양 끝으로 (`justify-content: space-between`) |
| Hero 버튼, 필터 버튼, 푸터 | **Flex** | 한 줄로 나열, 공간 부족하면 `flex-wrap`으로 줄바꿈 |
| About (이미지 + 글) | **Flex** | 모바일은 세로(`column`), 태블릿부터 가로(`row`)로 방향만 바꾸면 됨 |
| Projects 카드 `.projects-grid` | **Grid** | 카드들의 가로 · 세로 줄을 **똑같이 맞춰야** 함 |
| Skills 목록 | **Grid** | 2칸 → 3칸으로 칸 수만 바꾸면 됨 |

**내 코드 어디?** `style.css` 6번(네비게이션), 9번(Skills), 10번(Projects)

### Q9. `repeat(auto-fit, minmax(280px, 1fr))`은 무슨 뜻인가요?

**한 줄 답** : "카드는 **최소 280px**, 남는 공간은 **똑같이 나누고**, 칸 수는 **화면에 들어가는 만큼 자동**으로" 라는 뜻입니다.

- `minmax(280px, 1fr)` : 한 칸의 크기는 최소 280px ~ 최대 1fr(남은 공간 1몫)
- `auto-fit` : 들어갈 수 있는 칸 수를 자동 계산
- 그래서 **미디어 쿼리 없이도** 모바일 1칸 → 태블릿 2칸 → 데스크톱 3칸이 됩니다. (테스트로 확인함)

**꼬리질문 : `auto-fill`과 차이는?**
- 카드가 적을 때 차이가 납니다. `auto-fill`은 **빈 칸을 남겨두고**, `auto-fit`은 빈 칸을 접어서 **있는 카드를 늘립니다.**

### Q10. 모바일 퍼스트는 무엇이고 왜 썼나요?

**한 줄 답** : **모바일 스타일을 기본**으로 쓰고, 화면이 커질 때 `min-width` 미디어 쿼리로 **추가**하는 방식입니다.

```css
.nav-menu { flex-direction: column; }          /* 기본 = 모바일 */
@media (min-width: 768px) {
  .nav-menu { flex-direction: row; }           /* 태블릿 이상에서 덮어쓰기 */
}
```

- 이유 1 : 모바일 사용자가 가장 많음
- 이유 2 : 단순한 화면(1단)에서 복잡한 화면(다단)으로 **더해가는 것**이 빼는 것보다 코드가 짧고 쉬움
- 이유 3 : 모바일 기기가 불필요한 데스크톱 스타일을 덜 계산함

**브레이크포인트** : `768px` (태블릿 — 햄버거 숨기고 메뉴 가로 표시), `1024px` (데스크톱 — 글자 · 여백 확대)

### Q11. CSS 변수는 왜 썼고, 다크 모드는 어떻게 만들었나요?

**한 줄 답** : 색을 **변수 한 곳**에 모아두고, 다크 모드일 때는 **변수 값만 바꿔치기** 합니다.

```css
:root              { --color-bg: #ffffff; }   /* 라이트 */
[data-theme="dark"] { --color-bg: #0f172a; }   /* 다크 : 값만 덮어쓰기 */
body { background-color: var(--color-bg); }   /* 쓰는 곳은 그대로 */
```

- JS가 `<html data-theme="dark">`로 속성만 바꾸면, **나머지 CSS는 수정 없이** 전체 색이 바뀝니다.
- 다크 모드에서는 보라색이 밝아지므로, 버튼 글자색도 `--color-on-primary` 변수로 어둡게 바꿔 **가독성**을 지켰습니다.

### Q12. hover 효과와 transition은 어떻게 적용했나요?

**한 줄 답** : `:hover` 때 살짝 떠오르게(`transform`) + 그림자를 키우고, `transition`으로 0.3초 동안 **부드럽게** 변하게 했습니다.

- 적용 위치 : 버튼(`.btn`), 카드(`.project-card`, `.skill-card`), 메뉴 링크, 스크롤탑 버튼
- 속도는 `--transition: 0.3s ease` 변수로 통일
- `top`, `margin` 대신 `transform`을 쓴 이유 : 레이아웃을 다시 계산하지 않아서 **더 부드럽고 빠름**

### Q13. 고정 헤더 때문에 섹션 제목이 가려지지 않게 어떻게 했나요?

**한 줄 답** : 섹션에 `scroll-margin-top: var(--header-height)`를 줘서, **헤더 높이만큼 위에 여유를 두고** 멈추게 했습니다.

<br />

---

## 3. JavaScript 기초 — DOM & 이벤트

### Q14. `querySelector`로 선택하고 `addEventListener`로 연결하는 흐름을 설명해주세요.

**한 줄 답** : ① 요소를 **찾고** → ② 이벤트를 **등록**하고 → ③ 이벤트가 생기면 **함수가 실행**되어 DOM을 바꿉니다.

```js
const hamburger = document.querySelector('#hamburger');   // ① 찾기
hamburger.addEventListener('click', toggleMenu);          // ② 등록 ("클릭되면 toggleMenu 실행해줘")
const toggleMenu = () => {                                // ③ 실행 → 화면 변경
  navMenu.classList.toggle('active');
};
```

- `querySelector` : 조건에 맞는 **첫 번째** 요소 1개
- `querySelectorAll` : 맞는 요소 **전부** (NodeList → `forEach` 가능)
  - 예 : `document.querySelectorAll('a[href^="#"]')` → `#`으로 시작하는 링크 전부

### Q15. HTML `onclick` 대신 `addEventListener`를 쓴 이유는?

**한 줄 답** : **HTML(구조)과 JS(동작)를 분리**하고, 한 요소에 **여러 이벤트**를 붙일 수 있기 때문입니다.

- `onclick`은 HTML 안에 JS가 섞여서 관리가 어렵고, 같은 이벤트를 하나만 등록할 수 있습니다.
- `addEventListener`는 `{ passive: true }` 같은 옵션도 줄 수 있습니다.

### Q16. `defer`는 왜 붙였나요?

**한 줄 답** : HTML을 **끝까지 다 읽은 뒤에** JS를 실행해서, `querySelector`가 요소를 **못 찾는(null) 문제**를 막기 위해서입니다.

| 방식 | HTML 읽기 | JS 실행 시점 |
| --- | --- | --- |
| `<script>` (그냥) | JS 만나면 **멈춤** | 즉시 → 아래 요소 아직 없음 ⚠️ |
| `async` | 멈추지 않음 | 다운로드 끝나는 **아무 때나** (순서 보장 X) |
| `defer` ✅ | 멈추지 않음 | HTML 다 읽은 뒤, **순서대로** |

### Q17. `var` 대신 `const`, `let`을 쓴 이유는?

**한 줄 답** : `var`는 **블록(`{}`)을 무시**하고 **중복 선언**도 되어서 버그가 생기기 쉽기 때문입니다.

- 기본은 `const` (다시 대입 안 함 → 실수 방지)
- 값이 **바뀌어야 하는 상태**만 `let` : `theme`, `projectState`, `formErrors`
- 꼬리질문 : "`const` 배열/객체는 내용 수정이 되나요?" → **됩니다.** `const`는 "변수에 다른 값을 **다시 대입**하는 것"만 막습니다.

### Q18. `textContent`와 `innerHTML`의 차이, 어디에 썼나요?

**한 줄 답** : `textContent`는 **글자 그대로**, `innerHTML`은 **HTML 태그로 해석**해서 넣습니다.

| | 쓴 곳 | 이유 |
| --- | --- | --- |
| `textContent` | 에러 메시지, 성공 메시지, 다크 모드 아이콘, 연도 | 글자만 바꾸면 되고 **안전함** |
| `innerHTML` | 프로젝트 카드, 필터 버튼, 로딩/에러 박스 | 태그가 포함된 **HTML 덩어리**를 만들어야 함 |

**꼬리질문 : innerHTML은 위험하지 않나요?** → Q30 참고 (XSS 방지로 `escapeHTML` 사용)

### Q19. `classList.add / remove / toggle`은 각각 어디에 썼나요?

| 메서드 | 쓴 곳 | 동작 |
| --- | --- | --- |
| `toggle('active')` | 햄버거 메뉴 | 없으면 붙이고, 있으면 뗌 (열기 ↔ 닫기) |
| `toggle('scrolled', 조건)` | 헤더 | 조건이 true면 붙이고 false면 뗌 |
| `add('show')` / `remove('show')` | 스크롤탑 버튼 | 300px 기준으로 붙이기 / 떼기 |
| `add('visible')` | 스크롤 애니메이션 | 화면에 들어오면 붙이기 |
| `remove('active')` | `closeMenu()` | 메뉴 링크 클릭 시 강제로 닫기 |

- **JS는 클래스만 붙이고 떼고**, 실제 모양 변화는 **CSS가 담당**합니다. (역할 분리)

### Q20. 이벤트 종류별로 어디에 사용했나요?

| 이벤트 | 위치 | 하는 일 |
| --- | --- | --- |
| `click` | 햄버거, 다크 모드, 메뉴 링크, 스크롤탑, 필터, 재시도 | 버튼 동작 |
| `scroll` | `window` | 헤더 배경 · 스크롤탑 버튼 표시 |
| `input` | 폼 입력칸 | 에러가 떠 있는 칸 **실시간 재검사** |
| `blur` | 폼 입력칸 | 칸에서 벗어날 때 검사 |
| `submit` | 폼 | 전체 검사 후 성공 메시지 |

### Q21. `event.preventDefault()`는 어디서, 왜 썼나요?

**한 줄 답** : 브라우저가 원래 하려던 **기본 동작을 막고** 내가 원하는 동작을 하기 위해서입니다.

| 위치 | 막은 기본 동작 | 대신 한 것 |
| --- | --- | --- |
| 폼 `submit` | 페이지 **새로고침** + 서버 전송 | JS로 검사 → 성공 메시지 표시 |
| 메뉴 링크 `click` | `#about`으로 **뚝 끊기며 점프** | `scrollIntoView({ behavior: 'smooth' })` + 모바일 메뉴 닫기 |

<br />

---

## 4. 인터랙션 구현

### Q22. 햄버거 메뉴는 어떻게 동작하나요?

**한 줄 답** : 버튼 클릭 → `classList.toggle('active')` → CSS에서 `.nav-menu.active`만 **보이게** 합니다.

1. 모바일 기본 CSS : `.nav-menu`는 `opacity: 0; visibility: hidden;` (숨김)
2. 클릭 → `navMenu.classList.toggle('active')`
3. `.nav-menu.active { opacity: 1; visibility: visible; }` → 보임
4. 다시 클릭 → 클래스가 떼어져서 숨김
5. 햄버거 줄 3개도 `.active`가 붙으면 **X 모양**으로 회전
6. `aria-expanded`를 `true/false`로 바꿔 스크린리더에게 열림 상태 전달
7. 메뉴 링크를 누르면 `closeMenu()`로 자동 닫힘
8. 768px 이상에서는 CSS가 햄버거를 `display: none`, 메뉴는 항상 가로로 보이게 덮어씀

**꼬리질문 : `display: none` 대신 `opacity + visibility`를 쓴 이유?** → `display`는 `transition` 애니메이션이 안 되기 때문입니다.

### Q23. 부드러운 스크롤은 어떻게 했나요?

**한 줄 답** : CSS `scroll-behavior: smooth` + JS `scrollIntoView({ behavior: 'smooth' })` 두 가지를 함께 썼습니다.

- CSS만으로도 되지만, JS에서는 **이동 후 모바일 메뉴 닫기**까지 해야 해서 클릭 이벤트를 직접 처리했습니다.

### Q24. 스크롤 탑 버튼, 헤더 배경 변경은?

**한 줄 답** : `scroll` 이벤트에서 `window.scrollY`를 확인해서 기준값 이상이면 클래스를 붙입니다.

```js
const { scrollY } = window;
header.classList.toggle('scrolled', scrollY >= 60);    // 60px 이상 → 헤더 배경
if (scrollY >= 300) scrollTopBtn.classList.add('show'); // 300px 이상 → 버튼 표시
```

- 버튼 클릭 → `window.scrollTo({ top: 0, behavior: 'smooth' })`
- 페이지 로드 때도 `handleScroll()`을 한 번 실행 → **새로고침 시 중간 위치**여도 올바르게 표시
- 기준값은 `CONFIG`에 모아두고 README에 명시

### Q25. 스크롤 애니메이션은 왜 Intersection Observer를 썼나요?

**한 줄 답** : `scroll` 이벤트는 스크롤할 때마다 **수십 번 실행**되지만, Observer는 요소가 **화면에 들어올 때만** 브라우저가 알려줘서 **성능이 좋습니다.**

```js
const revealObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach(({ isIntersecting, target }) => {
    if (!isIntersecting) return;
    target.classList.add('visible');   // 등장!
    observer.unobserve(target);        // 한 번만 실행하고 감시 종료
  });
}, { threshold: 0.2 });                // 20% 보이면
```

- `threshold: 0.2` 이유 : 0이면 1px만 보여도 실행돼서 **사용자가 애니메이션을 못 봄**, 1이면 큰 요소는 **끝까지 안 나타날 수 있음**
- **동적으로 만든 카드**도 `renderProjects()` 안에서 `observeReveal()`로 다시 감시 등록
- `prefers-reduced-motion` 설정 사용자에게는 애니메이션을 끔 (접근성)

### Q26. 다크 모드 설정은 어떻게 유지되나요?

**한 줄 답** : 토글할 때 `localStorage`에 저장하고, 페이지가 열릴 때 **저장값을 먼저 읽어서** 적용합니다.

1. 시작 : `getInitialTheme()` → ① 저장값 있으면 사용 → ② 없으면 OS 다크 모드 설정 확인
2. 클릭 : `setTheme()` → `theme` 변경 → `localStorage.setItem('theme', 'dark')` → `renderTheme()`
3. 새로고침 : 1번이 다시 실행되며 저장값 `'dark'`를 읽음 → 유지!

- `localStorage`는 시크릿 모드 등에서 **에러가 날 수 있어** `try/catch`로 감쌌습니다.
- 개발자도구 → Application → Local Storage 에서 `theme` 값을 직접 보여줄 수 있습니다.

### Q27. 폼 검사는 어떻게 동작하나요?

**한 줄 답** : 칸마다 **검사 규칙 함수**를 두고, 결과(에러 문구)를 `formErrors` 상태에 저장한 뒤 **입력칸 아래에 표시**합니다.

| 칸 | 규칙 |
| --- | --- |
| 이름 | 비어있으면 X, 2자 미만 X |
| 이메일 | 비어있으면 X, `글자@글자.글자` 형식 아니면 X |
| 메시지 | 비어있으면 X, 10자 미만 X |

- **submit** : `event.preventDefault()` → 3칸 모두 검사 → 하나라도 틀리면 **첫 번째 틀린 칸에 커서 이동** → 모두 맞으면 성공 메시지 + `form.reset()`
- **input** : 이미 에러가 떠 있는 칸만 실시간 재검사 → **고치는 순간 에러가 사라짐** (처음 입력할 때부터 빨간 글씨가 뜨면 불편하니까)
- **blur** : 칸에서 나갈 때 검사
- `trim()` : 스페이스만 입력한 경우도 "빈 값"으로 처리

**꼬리질문 : 이메일 정규식 `/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/` 풀이?**
- `^` 시작 / `[^\s@]+` 공백·@가 아닌 글자 1개 이상 / `@` / 다시 글자 / `\.` 점 / 마지막 글자 **2개 이상** / `$` 끝

<br />

---

## 5. ES6+ 문법 & 배열 메서드

### Q28. 화살표 함수, 구조분해 할당, map/filter는 **왜** 필요하고 어떻게 썼나요?

#### 화살표 함수 `() => {}`
- **왜** : 코드가 짧아지고, 이벤트 콜백처럼 **짧은 함수**를 넘길 때 읽기 쉬움
- **어디** : 거의 모든 함수 (`const toggleMenu = () => { ... }`)
- 한 줄이면 `{}`와 `return` 생략 : `const formatDate = (iso) => new Date(iso).toLocaleDateString('ko-KR');`

#### 템플릿 리터럴 `` `${}` ``
- **왜** : 문자열 `+` 연결 없이 **HTML 모양 그대로** 쓰고 중간에 값을 넣을 수 있음
- **어디** : `createProjectCard()`에서 카드 HTML 생성

#### 구조분해 할당 `const { a, b } = 객체`
- **왜** : 객체에서 **필요한 값만 짧게 꺼내기** (`projectState.status`를 매번 안 써도 됨)
- **어디**
  ```js
  const { status, repos, filter } = projectState;                // 객체에서 꺼내기
  const { scrollY } = window;
  entries.forEach(({ isIntersecting, target }) => { ... });      // 매개변수에서 바로 꺼내기
  Object.entries(fields).forEach(([fieldName, input]) => { ... }); // 배열에서 꺼내기
  ```

#### `map` — 배열을 **같은 개수의 다른 배열로 변환**
- **왜** : `for`문 + `push` 없이 "A 배열 → B 배열" 변환을 한 줄로
- **어디**
  1. GitHub 원본 데이터 → 필요한 값만 담은 객체 (`html_url` → `url`)
  2. 저장소 객체 배열 → **카드 HTML 문자열 배열** → `.join('')`으로 합쳐 `innerHTML`

#### `filter` — 조건에 **맞는 것만 남기기**
- **어디** : 언어 필터 `repos.filter(({ language }) => language === filter)`
- 언어 목록 만들 때 `null` 제거 `.filter(Boolean)`

#### `forEach` — 배열을 **돌면서 일 시키기** (결과 배열 없음)
- **어디** : 모든 앵커 링크에 이벤트 등록, `.reveal` 요소들 Observer 등록

**꼬리질문 : `map`과 `forEach` 차이?** → `map`은 **새 배열을 돌려주고**, `forEach`는 **아무것도 돌려주지 않습니다(undefined).** 결과가 필요하면 `map`.

#### 그 외
- **스프레드** `{ ...projectState, ...changes }` : 기존 상태를 복사하고 바뀐 부분만 덮어쓰기
- **Set** `[...new Set(배열)]` : 중복 제거 (언어 목록)
- `every` : 폼 검사 결과가 **모두 true**인지 확인

<br />

---

## 6. 비동기 처리 & GitHub API

### Q29. fetch와 async/await로 어떻게 데이터를 가져왔나요?

**한 줄 답** : `async` 함수 안에서 `await fetch()`로 **응답을 기다리고**, `await response.json()`으로 **데이터로 바꾼 뒤** 상태를 바꿨습니다.

```js
const fetchRepos = async () => {
  setProjectState({ status: 'loading' });          // 1. 로딩 상태
  try {
    const response = await fetch(endpoint);         // 2. 요청 & 응답 기다리기
    if (!response.ok) throw new Error(...);         // 3. 404/403도 에러로 처리
    const data = await response.json();            // 4. JSON → JS 배열
    const repos = data.map(...);                    // 5. 필요한 값만 정리
    setProjectState({ status: repos.length === 0 ? 'empty' : 'success', repos });
  } catch (error) {
    setProjectState({ status: 'error', errorMessage: error.message }); // 6. 실패
  }
};
```

- **왜 비동기?** 서버 응답은 시간이 걸리는데, 기다리는 동안 **화면이 멈추면 안 되기** 때문입니다.
- `async/await`는 `.then().then()` 체인보다 **위에서 아래로 읽혀서** 이해가 쉽습니다.

### Q30. 로딩 / 성공 / 에러 / 빈 상태를 UI로 어떻게 표현했나요?

**한 줄 답** : `projectState.status` 값 하나로 상태를 정하고, `renderProjects()`가 그 값에 맞는 화면을 그립니다.

| status | 언제 | 화면 |
| --- | --- | --- |
| `'loading'` | 요청 시작 직후 | 빙글빙글 스피너 + "로딩 중..." |
| `'success'` | 저장소 1개 이상 | 필터 버튼 + 카드 목록 |
| `'empty'` | 저장소 0개 | "표시할 프로젝트가 없습니다" |
| `'error'` | 네트워크 끊김, 404, 403 등 | "프로젝트를 불러올 수 없습니다" + 원인 + **다시 시도** 버튼 |

- 상태를 `isLoading`, `isError` 여러 변수로 나누지 않고 **하나의 `status`로 관리** → "로딩 중인데 에러도 true" 같은 **모순 상태가 생기지 않음**
- 재시도 버튼 → `fetchRepos()`를 다시 호출 → 로딩부터 다시 시작

**시연 방법** (평가자에게 보여줄 때)
- 로딩 : 개발자도구 → Network → **Slow 3G** 로 새로고침
- 에러 : Network → **Offline** 체크 후 새로고침 → 다시 Online → **다시 시도** 클릭
- 빈 상태 : `CONFIG.GITHUB_USER`를 저장소 없는 계정으로 바꾸기

### Q31. `response.ok`는 왜 따로 확인했나요?

**한 줄 답** : `fetch`는 **404, 403 같은 실패 응답이 와도 에러를 던지지 않기** 때문입니다.

- `fetch`가 `catch`로 가는 경우는 **네트워크 자체가 실패**했을 때뿐입니다.
- 그래서 `response.ok`(200~299)가 아니면 직접 `throw new Error()`로 `catch`에 보냅니다.
- 403이면 "요청 한도 초과" 안내 → GitHub API는 로그인 없이 **시간당 60회** 제한

### Q32. try/catch는 왜 필요한가요?

**한 줄 답** : 에러가 나도 **프로그램이 멈추지 않고**, 사용자에게 **에러 화면을 보여주기** 위해서입니다.

- `try/catch`가 없으면 에러 시 로딩 스피너가 **영원히 돌기만** 합니다.

### Q33. innerHTML에 API 데이터를 넣으면 위험하지 않나요? (보안)

**한 줄 답** : 위험할 수 있어서 `escapeHTML()`로 `<`, `>` 같은 특수문자를 **글자로 바꾼 뒤** 넣었습니다.

- 저장소 설명에 `<img src=x onerror=alert(1)>` 같은 코드가 있으면 그대로 **실행될 수 있음** (XSS 공격)
- `<` → `&lt;` 로 바꾸면 태그가 아니라 **그냥 글자**로 보입니다. (샘플 데이터로 테스트함)
- 새 탭 링크에는 `rel="noopener noreferrer"`로 열린 페이지가 내 페이지를 조작하지 못하게 했습니다.

### Q34. 필터/재시도 버튼에 이벤트를 어떻게 연결했나요? (이벤트 위임)

**한 줄 답** : 버튼은 `innerHTML`로 **매번 새로 만들어져서**, 버튼 대신 **항상 있는 부모 요소에 한 번만** 이벤트를 붙였습니다.

```js
filterBar.addEventListener('click', (event) => {
  const button = event.target.closest('.filter-btn'); // 클릭한 곳에서 가장 가까운 버튼
  if (!button) return;                                // 버튼 사이 빈 곳 클릭은 무시
  setProjectState({ filter: button.dataset.filter }); // data-filter 값 읽기
});
```

- 클릭 이벤트는 자식 → 부모로 **올라가는(버블링)** 성질이 있어서 가능합니다.
- 장점 : 버튼이 100개여도 리스너는 1개, 다시 그려도 **재등록 필요 없음**

<br />

---

## 7. 상태 관리 패턴 (React로 가는 다리)

### Q35. "이벤트 → 상태 변경 → DOM 업데이트"가 어떻게 연결되나요?

**한 줄 답** : 이벤트 핸들러는 **상태만 바꾸고**, 화면은 **render 함수가 상태를 보고** 그립니다.

```
[사용자 행동]  →  [상태 변경 함수]      →  [상태 변수]           →  [render 함수]         →  [화면]
 토글 클릭      →  setTheme()          →  theme = 'dark'       →  renderTheme()        →  전체 색 변경
 페이지 로드    →  setProjectState()   →  status = 'loading'   →  renderProjects()     →  스피너
 필터 클릭      →  setProjectState()   →  filter = 'Python'    →  renderProjects()     →  카드 1개만
 폼 입력/제출   →  validateField()     →  formErrors.email=... →  renderFieldError()   →  빨간 에러 문구
```

**예시로 한 번 따라가기 (필터)**
1. 사용자가 "Python" 버튼 **클릭** (이벤트)
2. `setProjectState({ filter: 'Python' })` → `projectState.filter`가 `'Python'`으로 **변경** (상태)
3. `setProjectState` 안에서 `renderProjects()` 자동 호출
4. `renderProjects()`가 `repos.filter(...)`로 Python만 골라 **카드 다시 그림** (DOM 업데이트)

### Q36. 왜 이벤트에서 바로 DOM을 안 바꾸고 굳이 상태를 거치나요?

**한 줄 답** : 화면을 바꾸는 코드가 **한 곳(render)에만** 있어서, 화면이 이상할 때 **상태 값만 보면 원인을 알 수 있기** 때문입니다.

- 예 : 필터 클릭, 재시도, 첫 로드 — 이벤트는 3종류지만 화면을 그리는 곳은 `renderProjects()` **하나**
- 이벤트마다 DOM을 직접 바꾸면, 코드 여기저기서 화면을 건드려 **꼬이기 쉽습니다.**

### Q37. 이게 React와 어떤 관계인가요?

**한 줄 답** : React는 제가 **손으로 한 "상태 → 다시 그리기"를 자동으로** 해주는 도구입니다.

| 내 코드 (바닐라 JS) | React |
| --- | --- |
| `let theme` + `setTheme()` | `const [theme, setTheme] = useState()` |
| `setProjectState()` 안에서 `renderProjects()` **직접 호출** | `setState` 하면 **자동으로** 다시 그림 |
| `createProjectCard()` 함수가 HTML 문자열 반환 | **컴포넌트** `<ProjectCard />`가 JSX 반환 |
| `repos.map(createProjectCard).join('')` | `repos.map(repo => <ProjectCard {...repo} />)` |
| `addEventListener('click', ...)` | `onClick={...}` |
| `innerHTML` 통째로 교체 | 바뀐 부분만 비교해서 교체 (Virtual DOM) |
| `escapeHTML()` 직접 작성 | 기본으로 자동 이스케이프 |

> 더 깊은 질문("왜 프레임워크부터 안 배우나요?", "프레임워크가 뭔가요?")은 **Q47 · Q48** 참고

<br />

---

## 8. 기타 예상 질문

### Q38. `rem` 단위를 쓴 이유는?
- `rem`은 **브라우저 기본 글자 크기(16px) 기준**이라, 사용자가 글자 크기를 키우면 레이아웃도 함께 커집니다. (접근성)

### Q39. `box-sizing: border-box`는 왜?
- `width: 300px`에 padding, border가 **포함**되어 계산됩니다. 안 쓰면 padding만큼 박스가 커져서 계산이 헷갈립니다.

### Q40. 접근성은 무엇을 챙겼나요?
- 시맨틱 태그, `alt`, `label for`, `aria-label`(아이콘 버튼), `aria-expanded`(햄버거), `aria-live`(API 상태 변화 읽기), `aria-invalid`(에러 칸), `:focus-visible`(키보드 포커스 표시), `prefers-reduced-motion`(애니메이션 끄기)

### Q41. GitHub Pages 배포 시 주의한 점은?
- 경로를 모두 **상대 경로**(`css/style.css`)로 작성 → `x0cloud69.github.io/portfolio/` 처럼 **하위 폴더 주소**에서도 파일을 찾음
- `/css/style.css`(슬래시 시작)로 쓰면 `x0cloud69.github.io/css/...`를 찾아서 **깨집니다.**
- 파일 이름 대소문자 주의 (Windows는 구분 안 하지만 GitHub Pages 서버는 구분)

### Q42. 아쉬운 점 / 개선하고 싶은 점은?
1. 문의 폼이 실제로 전송되지 않음 → Formspree / EmailJS 연동
2. 다크 모드 사용자는 새로고침 순간 **잠깐 밝은 화면이 깜빡**일 수 있음 (JS가 `defer`라 HTML 그린 뒤 실행되기 때문) → `<head>`에 아주 짧은 인라인 스크립트로 먼저 적용하면 해결 가능
3. GitHub API 호출 결과를 `sessionStorage`에 캐싱하면 새로고침마다 요청하지 않아 **시간당 60회 제한**을 덜 소모
4. `main.js`가 길어져서 기능별 파일(`theme.js`, `projects.js`, `form.js`)로 나누면 관리가 쉬움 (ES Modules)

### Q43. 어떻게 테스트했나요?
- 개발자도구 **기기 모드**로 375px(모바일) / 768px(태블릿) / 1280px(데스크톱) 확인 → 자세한 방법은 **Q44**
- Network 탭 **Slow 3G / Offline**으로 로딩 · 에러 상태 확인
- 빈 칸 제출, 잘못된 이메일, 짧은 메시지 입력으로 폼 검사 확인
- 다크 모드 켜고 **새로고침**해서 유지 확인, Application 탭에서 localStorage 값 확인

### Q44. "모든 환경에서 레이아웃이 최적화되어 보인다"를 어떻게 확인했나요?

**한 줄 답** : 개발자도구 기기 모드로 폭을 바꿔가며 **브레이크포인트마다 정해둔 체크 항목**을 확인했고, 마지막엔 실제 휴대폰으로도 봤습니다.

#### ① 개발자도구 기기 모드 (주력 방법)

1. `F12` → 왼쪽 위 **기기 모양 아이콘** 클릭 (단축키 `Ctrl` + `Shift` + `M`)
2. 상단에서 크기를 바꾸거나, 화면 가장자리를 **천천히 드래그** → 레이아웃이 바뀌는 지점(768px, 1024px)이 눈으로 보임

| 폭 | 확인 항목 |
| --- | --- |
| **375px** 모바일 | 햄버거 보임 / 메뉴 숨김, 프로젝트 카드 **1열**, Skills 2칸, About 이미지가 글 **위**, 제목 1.75rem |
| **768px** 태블릿 | 햄버거 **사라짐** + 메뉴 가로 한 줄, 카드 **2열**, Skills 3칸, About 이미지가 글 **왼쪽** |
| **1280px** 데스크톱 | 카드 **3열**, 글자 · 여백 확대, 본문이 가운데 1120px 안으로 모임 |

#### ② "깨졌다"를 판단하는 기준 4가지

1. **가로 스크롤이 생기는가** (가장 흔한 실패) — 콘솔에서 확인, `false`면 정상
   ```js
   document.documentElement.scrollWidth > window.innerWidth
   ```
2. 글자 · 버튼이 화면 밖으로 **잘리는가**
3. 이미지가 **찌그러지거나 넘치는가** (`img { max-width: 100% }`로 방지)
4. 모바일에서 버튼이 손가락으로 누를 만큼 **큰가** (약 44px 이상)

#### ③ 실제 기기로 확인

- 같은 와이파이에서 : `ipconfig`로 IPv4 주소 확인 → 폰 브라우저에 `http://192.168.0.x:5500` 입력
- 배포 후에는 GitHub Pages 주소를 폰에서 열어보는 것이 가장 확실

### Q45. 모바일 · 태블릿 · 데스크톱의 차이는 무엇인가요?

**한 줄 답** : **화면 폭**과 **조작 방식(터치 vs 마우스)**의 차이이고, 브라우저는 기기 종류가 아니라 **폭만 보고** 판단합니다.

#### ① 기본 차이

| | 모바일 | 태블릿 | 데스크톱 |
| --- | --- | --- | --- |
| 대표 폭 | 320~767px | 768~1023px | 1024px 이상 |
| 기기 예 | 갤럭시, 아이폰 | 아이패드, 갤럭시탭 | 노트북, 모니터 |
| 조작 | 손가락(터치) | 손가락 | 마우스 + 키보드 |
| 화면 방향 | 대부분 세로 | 세로 / 가로 | 가로 |
| 한 줄에 들어가는 내용 | 1개 | 2개 | 3개 이상 |

> 중요한 건 **"기기 종류"가 아니라 "폭"**입니다. 브라우저는 아이패드인지 노트북인지 모르고 오직 폭이 768px 이상인지만 봅니다. 그래서 데스크톱에서 창을 좁히면 모바일 화면이 나옵니다.

#### ② 조작 방식이 만드는 차이

- 터치는 마우스보다 **정확하지 않음** → 모바일은 버튼을 크게(약 44px 이상), 간격을 넓게
- 터치에는 **hover가 없음** → hover 효과에만 의존하면 안 되고, 중요한 정보는 항상 보이게
- 모바일은 **공간이 좁음** → 메뉴를 햄버거 안에 숨김 / 데스크톱은 넉넉하니 모두 펼침

#### ③ 내 사이트에서 실제로 달라지는 것

| | 모바일 (375px) | 태블릿 (768px) | 데스크톱 (1280px) |
| --- | --- | --- | --- |
| 메뉴 | 햄버거 버튼 (눌러야 열림) | 가로로 펼쳐짐 | 가로로 펼쳐짐 |
| 프로젝트 카드 | 1열 | 2열 | 3열 |
| Skills | 2칸 | 3칸 | 3칸 |
| About | 이미지 위, 글 아래 | 이미지 왼쪽, 글 오른쪽 | 좌우 배치 + 여백 확대 |
| 제목 크기 | 1.75rem | 2.6rem | 3.4rem |

#### ④ 왜 하필 768px, 1024px인가요?

- 아이패드 세로가 768px, 가로가 1024px이라 **관행처럼 굳어진 값**입니다.
- 법으로 정해진 숫자가 아니라, **내 디자인이 깨지는 지점**을 골라 정하는 것이 원칙입니다.
- 답변 예시 : "아이패드 기준의 일반적인 관행값을 썼고, 폭을 드래그하며 확인했을 때 이 지점에서 레이아웃을 바꾸는 것이 자연스러웠습니다."

### Q46. 반응형은 소스의 어디에서 설정되나요?

**한 줄 답** : `index.html`의 **viewport 메타 태그 1줄**과, `style.css`의 **기본(모바일) 스타일 + 미디어 쿼리 2개**입니다.

#### ① HTML — 반응형의 스위치 (`index.html` 6번째 줄)

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
```

- `width=device-width` : 페이지 폭을 **기기 실제 폭**에 맞춤
- 이 줄이 없으면 폰이 화면을 980px로 가정해 **전체를 축소**해서 보여주고, 미디어 쿼리도 무의미해집니다.

#### ② CSS 기본값 = 모바일 (`style.css` 앞쪽, 미디어 쿼리 밖)

| 선택자 | 설정 | 결과 |
| --- | --- | --- |
| `.nav-menu` | `flex-direction: column` | 메뉴 세로 |
| `.about-inner` | `flex-direction: column` | 이미지 위, 글 아래 |
| `.skills-list` | `grid-template-columns: repeat(2, 1fr)` | 2칸 |
| `.hero-title` | `font-size: 1.75rem` | 작은 제목 |

#### ③ 태블릿 — `@media (min-width: 768px)` (15번 섹션)

| 선택자 | 덮어쓰는 값 |
| --- | --- |
| `.hamburger` | `display: none` (햄버거 숨김) |
| `.nav-menu` | `position: static` + `flex-direction: row` (가로 메뉴) |
| `.about-inner` | `flex-direction: row` |
| `.skills-list` | 3칸 |
| `.hero-title` | `2.6rem` |

#### ④ 데스크톱 — `@media (min-width: 1024px)` (16번 섹션)

- `--font-size-xl`, `--header-height` 변수 값 확대, `.hero-title` `3.4rem`, 여백 확대

#### ⑤ 미디어 쿼리 없이 알아서 반응하는 부분

| 코드 | 위치 | 역할 |
| --- | --- | --- |
| `repeat(auto-fit, minmax(280px, 1fr))` | `.projects-grid` | 카드가 폭에 따라 1 → 2 → 3열 자동 |
| `max-width: 1120px` | `.container` | 큰 모니터에서 너무 퍼지지 않게 |
| `max-width: 100%` | `img` | 이미지가 화면 밖으로 안 넘치게 |
| `flex-wrap: wrap` | 버튼 · 필터 묶음 | 공간 부족하면 다음 줄로 |

> 브레이크포인트를 바꾸고 싶다면 `style.css` 15 · 16번 섹션의 `768px` / `1024px` 숫자만 고치면 됩니다.

<br />

---

## 9. 요구사항 체크리스트 (평가표 대조용)

| 요구사항 | 구현 위치 | ✔ |
| --- | --- | --- |
| index.html / css / js / images 분리 | 폴더 구조 | ✅ |
| 시맨틱 태그 header, nav, main, section, article, footer | `index.html`, `createProjectCard()` | ✅ |
| Hero · About · Skills · Projects · Contact · Footer | `index.html` | ✅ |
| 앵커 링크 네비게이션 | `.nav-menu` | ✅ |
| 모든 이미지 의미 있는 alt | 프로필 이미지 | ✅ |
| label for–id 매칭 | Contact 폼 | ✅ |
| CSS 변수 `:root` / `[data-theme="dark"]` | `style.css` 1, 2번 | ✅ |
| 네비게이션 Flexbox | `.nav` | ✅ |
| Projects Grid auto-fit + minmax | `.projects-grid` | ✅ |
| 모바일 퍼스트, 768 / 1024px | `style.css` 15, 16번 | ✅ |
| 모든 환경에서 레이아웃 최적화 (확인 방법) | Q44 · Q45 · Q46 | ✅ |
| 모바일 햄버거 버튼 | `.hamburger` | ✅ |
| hover + transition, 카드 box-shadow | `.btn`, `.project-card` | ✅ |
| defer / const·let / onclick 없음 | `index.html`, `main.js` | ✅ |
| querySelector(All), textContent, innerHTML | `main.js` 전체 | ✅ |
| classList add / remove / toggle | Q19 표 | ✅ |
| click, submit, scroll, input 이벤트 | Q20 표 | ✅ |
| preventDefault | 폼 submit, 앵커 click | ✅ |
| 햄버거 toggle('active') | `toggleMenu()` | ✅ |
| 부드러운 스크롤 | 4번 섹션 | ✅ |
| 스크롤탑 300px / 헤더 60px (README 명시) | `CONFIG`, `handleScroll()` | ✅ |
| 다크 모드 + localStorage | 2번 섹션 | ✅ |
| Intersection Observer threshold 0.2 (README 명시) | 6번 섹션 | ✅ |
| 폼 필수값 · 이메일 형식 · 에러 위치 · 성공 메시지 | 8번 섹션 | ✅ |
| 화살표 함수 · 템플릿 리터럴 · 구조분해 | 전체 | ✅ |
| map(카드 변환) · filter(언어 필터) · forEach | 7번 섹션 | ✅ |
| fetch + async/await + try/catch | `fetchRepos()` | ✅ |
| 로딩 · 성공 · 에러(재시도) · 빈 상태 | `createStatusBox()` | ✅ |
| 상태 → 렌더링 흐름 3개 이상 | 4개 (Q35) | ✅ |
| GitHub Pages 배포 | README 6번 절차 | ⬜ 직접 진행 |
| README 설명 · 기술 · URL · 스크린샷 | `README.md` | ✅ (배포 후 URL 확인) |
