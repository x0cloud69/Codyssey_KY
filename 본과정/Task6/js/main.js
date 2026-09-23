/* =================================================================
   main.js
   -----------------------------------------------------------------
   이 파일 전체를 관통하는 규칙 한 줄 :

       "사용자 이벤트 → 상태(변수) 변경 → 화면(DOM) 업데이트"

   - 이벤트   : 사용자가 클릭/입력/스크롤 하는 것 (addEventListener로 감지)
   - 상태     : "지금 화면이 어떤 상태인지" 기억하는 변수 (theme, projectState, formErrors)
   - 화면 갱신 : 상태를 보고 DOM을 바꾸는 render 함수 (renderTheme, renderProjects ...)

   ※ HTML에서 defer로 불러오기 때문에, 이 코드가 실행될 때는
     이미 모든 HTML 요소가 만들어져 있다. (querySelector가 null이 안 됨)
   ※ var는 쓰지 않는다. 바뀌지 않는 값은 const, 바뀌는 값만 let.
   ================================================================= */


/* =================================================================
   0. 설정값 (여기 숫자만 바꾸면 동작 기준이 바뀐다 → README에도 적어둠)
   ================================================================= */
const CONFIG = {
  GITHUB_USER: 'x0cloud69',     // GitHub 아이디
  HEADER_SCROLL_OFFSET: 60,     // 이 값(px) 이상 스크롤하면 헤더 배경색 변경
  SCROLL_TOP_OFFSET: 300,       // 이 값(px) 이상 스크롤하면 "맨 위로" 버튼 표시
  REVEAL_THRESHOLD: 0.2,        // 요소가 20% 보이면 스크롤 애니메이션 실행
  THEME_STORAGE_KEY: 'theme',   // 로컬스토리지에 저장할 때 쓰는 이름(key)
};


/* =================================================================
   1. DOM 요소 선택 (querySelector)
   - 자주 쓰는 요소를 미리 변수에 담아두면 매번 찾지 않아도 된다.
   ================================================================= */
const html = document.documentElement;                  // <html> 태그
const header = document.querySelector('#header');
const navMenu = document.querySelector('#nav-menu');
const hamburger = document.querySelector('#hamburger');
const themeToggle = document.querySelector('#theme-toggle');
const scrollTopBtn = document.querySelector('#scroll-top');

const filterBar = document.querySelector('#filter-bar');
const projectsStatus = document.querySelector('#projects-status');
const projectsGrid = document.querySelector('#projects-grid');

const contactForm = document.querySelector('#contact-form');
const formSuccess = document.querySelector('#form-success');


/* =================================================================
   2. 다크 모드
   흐름 : [버튼 클릭] → theme 상태 변경 + 로컬스토리지 저장 → renderTheme()
   ================================================================= */

// 로컬스토리지는 "시크릿 모드" 등에서 에러가 날 수 있어서 try/catch로 감싼다.
const loadSavedTheme = () => {
  try {
    return localStorage.getItem(CONFIG.THEME_STORAGE_KEY); // 'dark' | 'light' | null
  } catch (error) {
    return null;
  }
};

const saveTheme = (value) => {
  try {
    localStorage.setItem(CONFIG.THEME_STORAGE_KEY, value);
  } catch (error) {
    // 저장이 안 되더라도 화면 전환은 계속 동작하게 그냥 넘어간다.
  }
};

// 처음 테마 정하기 : ① 저장된 값 → ② 없으면 OS 설정(다크 모드 사용 여부)
const getInitialTheme = () => {
  const savedTheme = loadSavedTheme();
  if (savedTheme) return savedTheme;

  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  return prefersDark ? 'dark' : 'light';
};

// ★ 상태 : 현재 테마
let theme = getInitialTheme();

// ★ 화면 갱신 : 상태(theme)를 보고 화면을 바꾼다
const renderTheme = () => {
  // <html data-theme="dark"> 로 바뀌면 CSS의 [data-theme="dark"] 변수가 적용된다
  html.setAttribute('data-theme', theme);

  const isDark = theme === 'dark';
  themeToggle.textContent = isDark ? '☀️' : '🌙';   // 버튼 아이콘 바꾸기
  themeToggle.setAttribute('aria-label', isDark ? '라이트 모드로 전환' : '다크 모드로 전환');
};

// ★ 상태 변경 함수 : 상태 바꾸기 → 저장 → 다시 그리기
const setTheme = (nextTheme) => {
  theme = nextTheme;
  saveTheme(theme);
  renderTheme();
};

// ★ 이벤트 연결
themeToggle.addEventListener('click', () => {
  setTheme(theme === 'dark' ? 'light' : 'dark');
});

renderTheme(); // 페이지가 열리자마자 한 번 그려준다 (새로고침해도 유지되는 이유)


/* =================================================================
   3. 햄버거 메뉴 (모바일)
   흐름 : [햄버거 클릭] → classList.toggle('active') → CSS가 메뉴를 보여줌/숨김
   ================================================================= */
const toggleMenu = () => {
  // toggle은 클래스가 없으면 붙이고, 있으면 뗀다. 결과로 "지금 붙어있는지(true/false)"를 돌려준다.
  const isOpen = navMenu.classList.toggle('active');
  hamburger.classList.toggle('active');  // 햄버거 아이콘도 X 모양으로

  // 스크린리더 사용자를 위해 열림/닫힘 상태도 알려준다
  hamburger.setAttribute('aria-expanded', isOpen);
  hamburger.setAttribute('aria-label', isOpen ? '메뉴 닫기' : '메뉴 열기');
};

const closeMenu = () => {
  navMenu.classList.remove('active');
  hamburger.classList.remove('active');
  hamburger.setAttribute('aria-expanded', 'false');
  hamburger.setAttribute('aria-label', '메뉴 열기');
};

hamburger.addEventListener('click', toggleMenu);


/* =================================================================
   4. 부드러운 스크롤
   흐름 : [메뉴 링크 클릭] → 기본 이동(뚝 끊기는 점프) 막기 → 부드럽게 스크롤
   ================================================================= */
const anchorLinks = document.querySelectorAll('a[href^="#"]'); // href가 #으로 시작하는 모든 링크

anchorLinks.forEach((link) => {
  link.addEventListener('click', (event) => {
    const targetId = link.getAttribute('href');        // 예: "#about"
    const targetSection = document.querySelector(targetId);
    if (!targetSection) return;                         // 대상이 없으면 아무것도 안 함

    event.preventDefault();                             // 브라우저 기본 동작(즉시 점프) 막기
    targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    closeMenu();                                        // 모바일 메뉴가 열려 있으면 닫기
  });
});


/* =================================================================
   5. 스크롤 이벤트 : 헤더 배경 변경 + 맨 위로 버튼
   ================================================================= */
const handleScroll = () => {
  const { scrollY } = window;   // 구조분해 할당 : window.scrollY 를 꺼내서 scrollY 변수로

  // (1) 60px 이상 → 헤더에 .scrolled 붙이기 (toggle의 두 번째 값이 true면 붙이고, false면 뗀다)
  header.classList.toggle('scrolled', scrollY >= CONFIG.HEADER_SCROLL_OFFSET);

  // (2) 300px 이상 → 맨 위로 버튼 보이기 (add / remove 사용)
  if (scrollY >= CONFIG.SCROLL_TOP_OFFSET) {
    scrollTopBtn.classList.add('show');
  } else {
    scrollTopBtn.classList.remove('show');
  }
};

// passive: true → "스크롤을 막지 않을게"라고 브라우저에 알려서 스크롤이 더 부드러워짐
window.addEventListener('scroll', handleScroll, { passive: true });
handleScroll(); // 새로고침했을 때 이미 중간 위치일 수도 있으니 한 번 실행

scrollTopBtn.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});


/* =================================================================
   6. 스크롤 애니메이션 (Intersection Observer)
   - scroll 이벤트로 매번 위치를 계산하는 대신,
     "이 요소가 화면에 들어오면 알려줘"라고 브라우저에게 맡기는 방식 → 성능이 좋다.
   ================================================================= */
const revealObserver = new IntersectionObserver(
  (entries, observer) => {
    entries.forEach(({ isIntersecting, target }) => { // 구조분해 할당
      if (!isIntersecting) return;          // 아직 화면에 안 들어왔으면 패스

      target.classList.add('visible');      // CSS가 투명→보임, 아래→제자리 로 애니메이션
      observer.unobserve(target);           // 한 번 보여줬으면 더 이상 감시하지 않음
    });
  },
  { threshold: CONFIG.REVEAL_THRESHOLD }    // 20% 이상 보일 때 실행
);

// 여러 요소를 한 번에 감시 등록하는 함수 (나중에 동적으로 만든 카드에도 재사용)
const observeReveal = (elements) => {
  elements.forEach((element) => revealObserver.observe(element));
};

observeReveal(document.querySelectorAll('.reveal'));


/* =================================================================
   7. Projects : GitHub API 연동
   흐름 : [페이지 로드 / 재시도 클릭] → status: 'loading'
          → fetch 성공 → status: 'success' 또는 'empty'
          → fetch 실패 → status: 'error'
          → 상태가 바뀔 때마다 renderProjects()가 화면을 다시 그림
   ================================================================= */

// ★ 상태 : Projects 섹션이 "지금 어떤 상태인지"
let projectState = {
  status: 'loading',  // 'loading' | 'success' | 'error' | 'empty'
  repos: [],          // 불러온 저장소 목록
  filter: 'all',      // 현재 선택된 언어 필터
  errorMessage: '',
};

// ★ 상태 변경 함수 : 바뀐 부분만 덮어쓰고(...스프레드) → 다시 그리기
//   (React의 setState와 같은 아이디어)
const setProjectState = (changes) => {
  projectState = { ...projectState, ...changes };
  renderProjects();
};

// API에서 받은 글자를 innerHTML에 넣기 전에 안전하게 바꾸기 (XSS 방지)
// 예: "<script>" → "&lt;script&gt;" (태그가 아니라 그냥 글자로 보이게)
const escapeHTML = (text) =>
  String(text).replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  })[char]);

// "2026-09-11T08:00:00Z" → "2026. 9. 11."
const formatDate = (isoString) => new Date(isoString).toLocaleDateString('ko-KR');

// 저장소 1개(객체) → 카드 HTML(문자열) 로 바꾸는 함수
// 매개변수 자리에서 바로 구조분해 할당으로 필요한 값만 꺼낸다
const createProjectCard = ({ name, description, url, language, stars, updatedAt }) => `
  <article class="project-card reveal">
    <h3>${escapeHTML(name)}</h3>
    <p class="project-desc">${escapeHTML(description || '설명이 없는 저장소입니다.')}</p>
    <div class="project-meta">
      <span class="project-lang">${escapeHTML(language || '기타')}</span>
      <span aria-label="스타 ${stars}개">⭐ ${stars}</span>
      <span>업데이트 ${formatDate(updatedAt)}</span>
    </div>
    <a class="project-link" href="${escapeHTML(url)}" target="_blank" rel="noopener noreferrer">
      GitHub에서 보기 →
    </a>
  </article>
`;

// 필터 버튼 HTML 만들기 : ['all', 'JavaScript', 'Python'] → 버튼 3개
const createFilterButtons = (repos, currentFilter) => {
  // map으로 언어만 뽑고 → filter로 빈 값(null) 제거 → Set으로 중복 제거
  const languages = [...new Set(repos.map(({ language }) => language).filter(Boolean))];
  const filters = ['all', ...languages];

  return filters
    .map((filter) => {
      const isActive = filter === currentFilter;
      const label = filter === 'all' ? '전체' : filter;
      return `
        <button type="button"
                class="filter-btn ${isActive ? 'active' : ''}"
                data-filter="${escapeHTML(filter)}"
                aria-pressed="${isActive}">
          ${escapeHTML(label)}
        </button>`;
    })
    .join('');
};

// 상태 메시지(로딩/에러/빈 상태) 박스 HTML
const createStatusBox = (status, errorMessage) => {
  if (status === 'loading') {
    return `
      <div class="status-box">
        <div class="spinner" aria-hidden="true"></div>
        <p>로딩 중...</p>
      </div>`;
  }

  if (status === 'error') {
    return `
      <div class="status-box status-error">
        <p>프로젝트를 불러올 수 없습니다.</p>
        <small>${escapeHTML(errorMessage)}</small>
        <button type="button" class="btn btn-primary retry-btn">다시 시도</button>
      </div>`;
  }

  // 'empty'
  return `
    <div class="status-box">
      <p>표시할 프로젝트가 없습니다.</p>
    </div>`;
};

// ★ 화면 갱신 : projectState를 보고 Projects 섹션 전체를 다시 그린다
const renderProjects = () => {
  const { status, repos, filter, errorMessage } = projectState; // 구조분해 할당

  // 1) 일단 싹 비우기
  filterBar.innerHTML = '';
  projectsStatus.innerHTML = '';
  projectsGrid.innerHTML = '';

  // 2) 성공이 아니면(로딩/에러/빈 상태) 메시지만 보여주고 끝
  if (status !== 'success') {
    projectsStatus.innerHTML = createStatusBox(status, errorMessage);
    return;
  }

  // 3) 성공 : 필터 적용 (filter 메서드)
  const visibleRepos =
    filter === 'all' ? repos : repos.filter(({ language }) => language === filter);

  filterBar.innerHTML = createFilterButtons(repos, filter);

  if (visibleRepos.length === 0) {
    projectsStatus.innerHTML = createStatusBox('empty');
    return;
  }

  // 4) 카드 그리기 : 배열 → map으로 HTML 문자열 배열 → join으로 하나로 합치기
  projectsGrid.innerHTML = visibleRepos.map(createProjectCard).join('');

  // 5) 새로 만든 카드에도 스크롤 애니메이션 연결
  observeReveal(projectsGrid.querySelectorAll('.reveal'));
};

// GitHub API 호출 (async/await)
const fetchRepos = async () => {
  setProjectState({ status: 'loading', errorMessage: '' }); // 요청 시작 → 로딩 상태

  const endpoint = `https://api.github.com/users/${CONFIG.GITHUB_USER}/repos?sort=updated&per_page=100`;

  try {
    // await : 응답이 올 때까지 "기다렸다가" 다음 줄로 간다
    const response = await fetch(endpoint);

    // fetch는 404, 403이어도 에러를 던지지 않는다 → 직접 확인해서 에러로 만든다
    if (!response.ok) {
      const reason = response.status === 403
        ? '요청 한도를 초과했어요. 잠시 후 다시 시도해주세요.'
        : `서버 응답 오류 (${response.status})`;
      throw new Error(reason);
    }

    const data = await response.json(); // 응답 본문(JSON)을 자바스크립트 배열로 변환

    // 필요한 값만 골라 새 객체로 정리 (map + 구조분해 할당)
    const repos = data.map(({ id, name, description, html_url, language, stargazers_count, updated_at }) => ({
      id,
      name,
      description,
      url: html_url,
      language,
      stars: stargazers_count,
      updatedAt: updated_at,
    }));

    // 받아온 게 0개면 'empty', 있으면 'success'
    setProjectState({
      status: repos.length === 0 ? 'empty' : 'success',
      repos,
      filter: 'all',
    });
  } catch (error) {
    // 인터넷 끊김, 잘못된 아이디, 한도 초과 등 모든 실패가 여기로 온다
    console.error('GitHub 저장소 불러오기 실패:', error);
    setProjectState({
      status: 'error',
      errorMessage: error.message || '네트워크 연결을 확인해주세요.',
    });
  }
};

/*
  이벤트 위임(Event Delegation)
  - 필터 버튼과 재시도 버튼은 innerHTML로 "매번 새로 만들어지기" 때문에
    버튼마다 addEventListener를 붙이면 다시 그릴 때마다 또 붙여야 한다.
  - 그래서 "항상 존재하는 부모"에 한 번만 붙이고, 클릭된 대상(event.target)을 확인한다.
*/
filterBar.addEventListener('click', (event) => {
  const button = event.target.closest('.filter-btn'); // 클릭한 곳에서 가장 가까운 필터 버튼 찾기
  if (!button) return;

  setProjectState({ filter: button.dataset.filter }); // 필터 상태 변경 → 목록 다시 그리기
});

projectsStatus.addEventListener('click', (event) => {
  if (event.target.closest('.retry-btn')) {
    fetchRepos(); // 재시도
  }
});

fetchRepos(); // 페이지 열리면 바로 불러오기


/* =================================================================
   8. 문의 폼 유효성 검사
   흐름 : [입력/제출] → 검사 → formErrors 상태 변경 → 에러 메시지 표시/숨김
   ================================================================= */

// 이메일 형식 : "글자@글자.글자(2자 이상)"
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

// 검사할 입력칸들
const fields = {
  name: document.querySelector('#name'),
  email: document.querySelector('#email'),
  message: document.querySelector('#message'),
};

// 칸마다 검사 규칙 : 문제가 있으면 "에러 문구", 없으면 "" (빈 문자열) 을 돌려준다
const validators = {
  name: (value) => {
    if (value.trim() === '') return '이름을 입력해주세요.';
    if (value.trim().length < 2) return '이름은 2자 이상 입력해주세요.';
    return '';
  },
  email: (value) => {
    if (value.trim() === '') return '이메일을 입력해주세요.';
    if (!EMAIL_PATTERN.test(value.trim())) return '올바른 이메일 형식이 아닙니다. (예: you@example.com)';
    return '';
  },
  message: (value) => {
    if (value.trim() === '') return '메시지를 입력해주세요.';
    if (value.trim().length < 10) return '메시지는 10자 이상 입력해주세요.';
    return '';
  },
};

// ★ 상태 : 칸별 에러 문구
let formErrors = { name: '', email: '', message: '' };

// ★ 화면 갱신 : 한 칸의 에러 상태를 화면에 반영
const renderFieldError = (fieldName) => {
  const input = fields[fieldName];
  const errorElement = document.querySelector(`#${fieldName}-error`);
  const message = formErrors[fieldName];
  const hasError = message !== '';

  errorElement.textContent = message;                 // 입력칸 바로 아래에 에러 문구
  input.classList.toggle('invalid', hasError);        // 빨간 테두리 on/off
  input.setAttribute('aria-invalid', hasError);       // 스크린리더에게도 알려주기
};

// 한 칸 검사 → 상태 변경 → 화면 갱신. 통과하면 true를 돌려준다
const validateField = (fieldName) => {
  const message = validators[fieldName](fields[fieldName].value);
  formErrors = { ...formErrors, [fieldName]: message };  // [fieldName] : 변수 값을 키 이름으로 사용
  renderFieldError(fieldName);
  return message === '';
};

// 칸마다 이벤트 연결 (Object.entries로 [이름, 요소] 쌍을 꺼내 forEach로 순회)
Object.entries(fields).forEach(([fieldName, input]) => {
  // input 이벤트 : 글자를 칠 때마다 발생
  input.addEventListener('input', () => {
    formSuccess.textContent = '';               // 다시 입력하면 이전 성공 메시지는 지우기
    // 이미 에러가 떠 있는 칸만 실시간 재검사 → 올바르게 고치는 순간 에러가 사라진다
    // (처음 타이핑할 때부터 빨간 글씨가 뜨면 불편하니까)
    if (formErrors[fieldName]) validateField(fieldName);
  });

  // blur 이벤트 : 입력칸에서 벗어날 때 → 이때 한 번 검사
  input.addEventListener('blur', () => {
    if (input.value !== '') validateField(fieldName);
  });
});

// submit 이벤트 : "보내기" 버튼 클릭 또는 Enter
contactForm.addEventListener('submit', (event) => {
  event.preventDefault(); // ★ 기본 동작(페이지 새로고침 + 서버 전송) 막기

  // 모든 칸 검사 (map으로 결과 [true, false, true] 모으기 → every로 전부 true인지 확인)
  const results = Object.keys(fields).map(validateField);
  const isFormValid = results.every((isValid) => isValid);

  if (!isFormValid) {
    formSuccess.textContent = '';
    // 첫 번째로 틀린 칸에 커서를 옮겨준다
    const firstInvalidField = Object.keys(fields).find((fieldName) => formErrors[fieldName]);
    fields[firstInvalidField].focus();
    return;
  }

  // 모두 통과 → 성공 메시지 (실제 전송은 서버가 없으므로 생략)
  const { name } = Object.fromEntries(new FormData(contactForm)); // 폼 값 → 객체 → name만 꺼내기
  formSuccess.textContent = `${name.trim()}님, 메시지가 전송되었습니다! 곧 답장 드릴게요 😊`;
  contactForm.reset(); // 입력칸 비우기
});


/* =================================================================
   9. 기타 : 푸터 연도, GitHub 아이디 표시
   ================================================================= */
document.querySelector('#year').textContent = new Date().getFullYear();
document.querySelector('#github-user').textContent = `@${CONFIG.GITHUB_USER}`;
document.querySelector('#footer-github').href = `https://github.com/${CONFIG.GITHUB_USER}`;
