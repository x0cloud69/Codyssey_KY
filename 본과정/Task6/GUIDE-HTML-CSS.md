# 내 코드 읽는 법 — HTML · CSS 입문 가이드

> HTML/CSS를 처음 보는 상태에서, **내 포트폴리오 코드를 직접 짚어가며** 흐름을 파악하는 문서입니다.
> VS Code에서 `index.html`과 `css/style.css`를 옆에 띄워놓고 함께 보세요.

---

## 0. 큰 그림 — 웹페이지는 3개로 나뉜다

| 파일 | 역할 | 비유 |
| --- | --- | --- |
| `index.html` | **무엇이** 있는지 (제목, 글, 버튼, 이미지) | 집의 뼈대와 방 배치 |
| `css/style.css` | **어떻게 보이는지** (색, 크기, 위치, 여백) | 벽지 · 가구 · 인테리어 |
| `js/main.js` | **어떻게 움직이는지** (클릭하면 열리고 닫히고) | 전기 배선과 스위치 |

브라우저가 일하는 순서는 이렇습니다.

```
① index.html 을 위에서 아래로 읽는다
   ↓ <link rel="stylesheet" href="css/style.css"> 를 만나면
② style.css 를 읽어서 "어떻게 칠할지" 규칙을 외운다
   ↓ 규칙대로 화면을 그린다
③ HTML을 다 읽으면 main.js 를 실행한다 (defer 때문에 맨 마지막)
   ↓ 이제부터 클릭·스크롤에 반응한다
```

**핵심 감각 하나**: HTML은 "상자를 만드는 일", CSS는 "그 상자를 꾸미는 일"입니다. HTML만 있으면 흰 바탕에 검은 글씨만 쭉 나옵니다. 실제로 확인해보고 싶으면 `index.html` 14번째 줄 `<link ...>`를 잠시 지워보세요. 디자인이 전부 사라집니다. (확인했으면 되돌리기 `Ctrl+Z`)

---

## 1. HTML 문법 — 딱 4가지만 알면 읽힌다

### ① 태그는 여는 것과 닫는 것이 짝이다

```html
<h1>개발자 KY입니다</h1>
 ↑여는 태그        ↑닫는 태그 (슬래시 /)
```

여는 태그와 닫는 태그 **사이에 있는 것이 그 태그의 내용**입니다.

### ② 속성 = 태그에 주는 추가 정보

```html
<a href="#about" class="nav-link">About</a>
   ↑속성이름 ↑값     ↑속성이름  ↑값
```

- `href="#about"` → 눌렀을 때 갈 곳
- `class="nav-link"` → **CSS가 찾아올 때 쓰는 이름표** (제일 중요!)
- `id="hamburger"` → **JS가 찾아올 때 쓰는 이름표** (한 페이지에 하나뿐인 이름)

### ③ 태그 안에 태그를 넣는다 (중첩)

들여쓰기가 곧 **포함 관계**입니다.

```html
<header>              ← 바깥 상자
  <nav>               ← 그 안의 상자
    <ul>              ← 또 그 안
      <li>About</li>  ← 알맹이
    </ul>
  </nav>
</header>
```

코드를 읽을 때 **들여쓰기 칸 수만 보면 "무엇이 무엇 안에 있는지"** 알 수 있습니다.

### ④ 닫는 태그가 없는 태그도 있다

`<img />`, `<br />`, `<meta />`, `<input />` 처럼 내용이 없는 태그는 혼자 씁니다.

> 주석(설명 메모)은 `<!-- 이렇게 -->` 씁니다. 화면에는 안 보여요.

---

## 2. `index.html` 따라 읽기

### 2-1. `<head>` — 화면에 안 보이는 "설정" 구역 (3~22번째 줄)

```html
<head>
  <meta charset="UTF-8" />                            ← 한글이 깨지지 않게
  <meta name="viewport" content="width=device-width..."/> ← 폰에서 폭을 맞춤 (반응형 필수)
  <title>KY | Portfolio</title>                       ← 브라우저 탭에 뜨는 이름
  <link rel="stylesheet" href="css/style.css" />      ← CSS 파일 연결 ★
  <script src="js/main.js" defer></script>            ← JS 파일 연결 ★
</head>
```

`head` 안의 내용은 **화면에 보이지 않습니다.** 사람이 보는 것은 전부 `<body>` 안에 있어요.

### 2-2. `<body>` — 실제로 보이는 구역

body는 딱 3덩어리입니다.

```html
<body>
  <header> ... </header>   ← ① 맨 위 (로고 + 메뉴) — 스크롤해도 고정
  <main>   ... </main>     ← ② 본문 (Hero/About/Skills/Projects/Contact)
  <footer> ... </footer>   ← ③ 맨 아래 (저작권, 소셜 링크)
  <button class="scroll-top"> ← ④ 맨 위로 가는 동그란 버튼 (화면 구석에 떠 있음)
</body>
```

이 4덩어리 구조만 머리에 넣으면, 긴 코드도 "지금 내가 어디쯤 읽고 있는지" 알 수 있습니다.

### 2-3. `<main>` 안은 섹션들의 나열

```html
<main>
  <section id="hero">     ← 첫 화면 인사
  <section id="about">    ← 자기소개
  <section id="skills">   ← 기술 목록
  <section id="projects"> ← 프로젝트 카드
  <section id="contact">  ← 문의 폼
</main>
```

`section`은 "한 주제 덩어리"라는 뜻의 태그입니다. 그리고 각 섹션의 `id`는 **메뉴 링크와 짝**이에요.

```html
<a href="#about">About</a>      ← 이 링크를 누르면
<section id="about">            ← 같은 이름의 이 섹션으로 이동
```

`#`은 "같은 페이지 안에서 이 id를 찾아가라"는 뜻입니다.

### 2-4. 섹션 하나를 뜯어보기 (About)

```html
<section class="section about" id="about">      ← ① 섹션 전체
  <div class="container">                       ← ② 가운데 정렬 상자
    <h2 class="section-title reveal">About Me</h2>  ← ③ 제목
    <div class="about-inner">                   ← ④ 이미지 + 글을 묶는 상자
      <img src="images/profile.svg" alt="..." /> ← ⑤ 사진
      <div class="about-text">                  ← ⑥ 글 묶음
        <p>저는 ...</p>                          ← ⑦ 문단
      </div>
    </div>
  </div>
</section>
```

모든 섹션이 **①섹션 → ②container → ③제목 → ④내용** 이라는 같은 뼈대를 씁니다. 하나만 이해하면 나머지도 똑같아요.

여기서 `div`는 **아무 의미 없는 그냥 상자**입니다. "여러 개를 하나로 묶어서 한꺼번에 배치하고 싶을 때" 씁니다.

### 2-5. 자주 나오는 태그 사전

| 태그 | 뜻 | 내 코드에서 |
| --- | --- | --- |
| `<h1>`~`<h3>` | 제목 (숫자가 작을수록 큼) | h1=Hero 제목, h2=섹션 제목, h3=카드 제목 |
| `<p>` | 문단 (글) | 자기소개, 설명글 |
| `<a>` | 링크 | 메뉴, GitHub 링크 |
| `<img>` | 이미지 | 프로필 사진 |
| `<ul>` `<li>` | 목록 / 목록 항목 | 메뉴, Skills |
| `<button>` | 버튼 | 햄버거, 다크모드, 보내기 |
| `<form>` `<input>` `<label>` | 입력 양식 | Contact 폼 |
| `<div>` | 의미 없는 묶음 상자 | 레이아웃용 |
| `<span>` | 글자 중 일부만 묶는 상자 | `KY`만 보라색으로 |

---

## 3. CSS 문법 — 규칙 하나의 생김새

```css
.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 999px;
}
```

읽는 법: **"`.btn` 이라는 이름표가 붙은 것들은 / 안쪽 여백을 이만큼 주고 / 모서리를 둥글게 해라"**

```
.btn      {  padding  :  0.75rem 1.5rem ;  }
 ↑선택자      ↑속성        ↑값              ↑;로 한 줄 끝
 (누구를)     (무엇을)      (어떻게)
```

### 선택자 — "누구를 꾸밀지" 고르는 방법

| 쓰는 법 | 의미 | 예 |
| --- | --- | --- |
| `.이름` | **class**가 이 이름인 것 전부 | `.btn` → class="btn"인 버튼 모두 |
| `#이름` | **id**가 이 이름인 것 하나 | `#header` |
| `태그이름` | 그 태그 전부 | `img { }` → 모든 이미지 |
| `.a .b` | `.a` 안에 있는 `.b` | `.nav-logo span` |
| `.a.b` (붙여씀) | `.a`와 `.b`를 **둘 다** 가진 것 | `.header.scrolled` |
| `.a:hover` | 마우스를 올렸을 때의 `.a` | `.btn:hover` |

### HTML과 CSS가 연결되는 지점 ★

이게 가장 중요한 감각입니다. **class 이름이 두 파일을 잇는 다리**예요.

```html
<!-- index.html -->
<a href="#projects" class="btn btn-primary">프로젝트 보기</a>
                           ↑         ↑
                     이름표 2개를 동시에 붙일 수 있다 (띄어쓰기로 구분)
```

```css
/* style.css */
.btn         { padding: 0.75rem 1.5rem; border-radius: 999px; }  ← 모든 버튼 공통 모양
.btn-primary { background-color: var(--color-primary); }         ← 이 버튼만 보라색 배경
```

→ 결과: 그 링크는 **공통 모양 + 보라색**을 둘 다 적용받습니다. 공통은 `.btn`에 모아두고, 다른 점만 `.btn-primary` / `.btn-outline`으로 나누는 것이 CSS의 기본 작성 요령이에요.

---

## 4. `style.css` 읽는 순서

파일 맨 위 주석에 **1~16번 목차**가 있습니다. 필요한 곳만 찾아가면 됩니다.

| 번호 | 내용 | 언제 열어볼까 |
| --- | --- | --- |
| 1 | CSS 변수 (색, 글자, 간격) | **색을 바꾸고 싶을 때** |
| 2 | 다크 모드 색 | 다크 모드 색만 바꿀 때 |
| 3 | 기본 초기화 | 거의 안 건드림 |
| 4 | 공통 레이아웃 (container, section) | 전체 여백 조절 |
| 5 | 버튼 | 버튼 모양 |
| 6 | 헤더 · 메뉴 · 햄버거 | 상단 바 |
| 7~13 | Hero / About / Skills / Projects / Contact / Footer | 해당 섹션 |
| 14 | 스크롤 애니메이션 | 등장 효과 |
| 15 | **태블릿(768px~)** | 태블릿에서 다르게 보이게 |
| 16 | **데스크톱(1024px~)** | 데스크톱에서 다르게 보이게 |

### 4-1. CSS 변수 — 색깔 저장소 (1번 섹션)

```css
:root {
  --color-primary: #6366f1;   /* 이름을 붙여서 저장 */
}

.btn-primary {
  background-color: var(--color-primary);   /* 저장한 값을 꺼내 쓴다 */
}
```

- `--이름: 값;` 으로 **저장**하고, `var(--이름)` 으로 **꺼내 씁니다.**
- 사이트 전체 보라색을 초록색으로 바꾸고 싶으면? **1번 섹션의 `--color-primary` 한 줄만** 고치면 버튼·링크·강조 글자가 전부 바뀝니다.
- `#6366f1`은 색상 코드예요. VS Code에서 그 코드 왼쪽의 작은 네모를 클릭하면 색상 선택기가 뜹니다.

### 4-2. 박스 모델 — 모든 요소는 네모 상자

CSS에서 여백은 두 종류이고, 이 둘을 헷갈리면 화면이 뜻대로 안 나옵니다.

```
┌─────────── margin (상자 바깥 여백 = 옆 상자와의 거리) ───────────┐
│  ┌──────── border (테두리 선) ─────────┐                        │
│  │  ┌───── padding (상자 안쪽 여백) ──┐ │                        │
│  │  │        내용 (글, 이미지)        │ │                        │
│  │  └────────────────────────────────┘ │                        │
│  └─────────────────────────────────────┘                        │
└──────────────────────────────────────────────────────────────────┘
```

- **안쪽을 넓히고 싶다** (버튼을 크게) → `padding`
- **다른 것과 떨어뜨리고 싶다** → `margin`

값 쓰는 법: `padding: 10px 20px;` → **위아래 10px, 좌우 20px**. 값이 하나면 사방 전부.

### 4-3. Flexbox — 한 줄로 나란히 (6번 섹션)

```css
.nav {
  display: flex;                    /* 자식들을 가로로 나란히 */
  align-items: center;              /* 세로 가운데 정렬 */
  justify-content: space-between;   /* 첫째는 왼쪽 끝, 마지막은 오른쪽 끝 */
}
```

```
[로고]                                    [메뉴] [🌙] [☰]
 ↑ 왼쪽 끝                                        오른쪽 끝 ↑
```

`display: flex`를 **부모에게** 주면, **자식들**이 나란히 서는 구조입니다. (자식에게 주는 게 아니에요!)

- `flex-direction: column` → 가로 말고 **세로**로 나열
- `gap: 16px` → 자식들 사이 간격

### 4-4. Grid — 바둑판으로 배치 (10번 섹션)

```css
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}
```

읽는 법: **"칸 하나는 최소 280px, 화면에 들어가는 만큼 자동으로 칸 수를 정해라."**

```
모바일(375px)  [카드]              ← 280px짜리가 1개밖에 안 들어감
태블릿(768px)  [카드][카드]         ← 2개
데스크톱(1280) [카드][카드][카드]    ← 3개
```

이 한 줄 덕분에 **미디어 쿼리 없이도** 카드 개수가 자동으로 바뀝니다.

### 4-5. 반응형 — 미디어 쿼리 (15, 16번 섹션)

```css
.skills-list { grid-template-columns: repeat(2, 1fr); }   /* 기본(모바일) = 2칸 */

@media (min-width: 768px) {                                /* 화면이 768px 이상이면 */
  .skills-list { grid-template-columns: repeat(3, 1fr); }  /* 3칸으로 덮어쓰기 */
}
```

`@media (min-width: 768px) { ... }` = **"화면 폭이 768px 이상일 때만 이 안의 규칙을 적용해라."**

CSS는 **아래에 쓴 것이 위를 덮어씁니다.** 그래서 미디어 쿼리를 파일 맨 끝에 두는 거예요.

---

## 5. 하나를 끝까지 추적해보기 — 햄버거 버튼 ☰

세 파일이 어떻게 이어지는지, 실제 기능 하나로 따라가 봅니다.

**① HTML — 버튼과 메뉴를 만든다** (`index.html`)

```html
<ul class="nav-menu" id="nav-menu"> ... </ul>       ← 메뉴 (이름표: nav-menu)
<button class="hamburger" id="hamburger"> ☰ </button> ← 버튼 (이름표: hamburger)
```

**② CSS — 평소엔 숨기고, `active`가 붙으면 보이게 한다** (`style.css` 6번 섹션)

```css
.nav-menu         { opacity: 0; visibility: hidden; }   /* 기본: 안 보임 */
.nav-menu.active  { opacity: 1; visibility: visible; }  /* active가 붙으면: 보임 */
```

**③ JS — 클릭되면 `active`라는 이름표를 붙였다 뗐다 한다** (`main.js` 3번 섹션)

```js
hamburger.addEventListener('click', () => {
  navMenu.classList.toggle('active');   // 없으면 붙이고, 있으면 뗀다
});
```

**④ 결과**

```
사용자가 ☰ 클릭
   → JS가 <ul class="nav-menu">를 <ul class="nav-menu active">로 바꿈
   → CSS의 `.nav-menu.active` 규칙이 발동
   → 메뉴가 나타남
```

**여기가 핵심입니다.** JS는 직접 색이나 위치를 바꾸지 않아요. **이름표(class)만 붙였다 뗐다** 하고, 실제 모양 변화는 CSS가 담당합니다. 다크 모드, 스크롤 버튼, 등장 애니메이션 전부 같은 원리예요.

개발자도구(F12)에서 햄버거를 클릭해보면, HTML 코드에 `active`가 **실시간으로 붙었다 사라지는 것**이 보입니다. 꼭 한 번 해보세요.

---

## 6. 직접 해보는 연습 5개

Live Server로 열어두고 파일을 저장하면 즉시 화면에 반영됩니다.

| # | 해볼 것 | 어디를 고치나 | 배우는 것 |
| --- | --- | --- | --- |
| 1 | 이름을 다른 이름으로 바꾸기 | `index.html`의 `KY` 글자 | HTML은 내용을 담당 |
| 2 | 사이트 전체 색을 초록으로 | `style.css` 1번 섹션 `--color-primary: #16a34a;` | CSS 변수의 힘 |
| 3 | Skills 카드 1개 추가 | `index.html`의 `<li class="skill-card">` 통째로 복사해서 붙여넣기 | 태그 구조 이해 |
| 4 | 카드 최소 너비를 400px로 | `.projects-grid`의 `minmax(280px, 1fr)` → `minmax(400px, 1fr)` | Grid 자동 배치 |
| 5 | `<link rel="stylesheet">` 줄 지워보기 | `index.html` 14번째 줄 | CSS가 없으면 어떻게 되는지 체감 |

> 망가져도 괜찮습니다. `Ctrl+Z`로 되돌리면 돼요. **직접 고쳐보는 것이 제일 빨리 느는 방법**입니다.

---

## 7. 막혔을 때 쓰는 개발자도구 (F12)

1. 바꾸고 싶은 부분에 **마우스 오른쪽 → 검사** 클릭
2. 왼쪽에 **그 부분의 HTML**, 오른쪽에 **적용된 CSS 규칙**이 보입니다
3. 오른쪽에서 숫자나 색을 직접 바꿔보면 **화면이 즉시 바뀝니다** (새로고침하면 사라지는 임시 실험)
4. 원하는 모양을 찾으면, 그 값을 실제 `style.css`에 옮겨 적으면 끝

"이 여백은 어디서 오는 거지?" 싶을 때 이 방법이 가장 빠릅니다.

---

## 8. 한 장 요약

```
index.html  →  "무엇이 있는가"  →  태그로 상자를 만들고 class 이름표를 붙인다
                                         ↓ (class 이름표로 연결)
style.css   →  "어떻게 보이는가" →  이름표를 찾아 색·크기·위치를 정한다
                                         ↓ (JS가 이름표를 붙였다 뗐다)
main.js     →  "어떻게 움직이는가" → 클릭·스크롤에 반응해 class를 바꾼다
```

- HTML에서 `class="___"`를 보면 → `style.css`에서 `.___`를 찾으면 그 모양 규칙이 있다
- HTML에서 `id="___"`를 보면 → `js/main.js`에서 `#___`를 찾으면 그 동작이 있다

이 두 줄이 이 프로젝트 코드를 읽는 지도입니다.
