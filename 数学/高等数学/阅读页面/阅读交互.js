/* 高等数学离线阅读页。内容由生成脚本嵌入，不依赖 fetch 或服务器。 */
(() => {
  'use strict';
  const pages = JSON.parse(document.getElementById('chapter-data').textContent);
  const chapters = pages.filter(page => page.kind === 'chapter');
  const topics = pages.filter(page => page.kind === 'topic');
  const $ = id => document.getElementById(id);
  const main = $('main-content');
  const layout = $('layout');
  const rail = $('reading-rail');
  const store = {
    get(key, fallback = '') { try { return localStorage.getItem(key) || fallback; } catch (_) { return fallback; } },
    set(key, value) { try { localStorage.setItem(key, value); } catch (_) {} },
  };
  const escape = value => String(value).replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[character]));
  const arrow = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 12h15m-5-5 5 5-5 5"/></svg>';
  let current = 'overview';
  let mode = store.get('calculus-mode', 'summary');
  if (!['summary', 'full'].includes(mode)) mode = 'summary';
  let tocItems = [];
  let routeNumber = 0;
  let mathQueue = Promise.resolve();
  let mathFailed = false;
  let pendingQuery = '';
  const kindLabel = { chapter: '章节笔记', topic: '补充理解', practice: '自测与解析', formula: '公式速查' };

  function tags(items) {
    return '<div class="tags">' + items.map(tag => '<span class="tag">' + escape(tag) + '</span>').join('') + '</div>';
  }
  function navGroup(label, items) {
    return '<div class="nav-label">' + label + '</div>' + items.map(page =>
      '<button class="nav-link" data-page="' + page.id + '"><span class="nav-number">' + page.number +
      '</span><span>' + escape(page.title) + '</span></button>').join('');
  }
  $('chapter-nav').innerHTML = navGroup('CHAPTERS / 十章笔记', chapters) +
    navGroup('EXPLORE / 补充理解', topics) +
    navGroup('REVIEW / 练习与速查', pages.filter(page => ['practice', 'formula'].includes(page.kind)));

  function closeMenu() {
    $('sidebar').classList.remove('open');
    $('mobile-shade').classList.remove('show');
    $('menu-btn').setAttribute('aria-expanded', 'false');
  }
  function navigate(id) {
    if (location.hash === '#' + id) render();
    else location.hash = id;
    closeMenu();
  }
  document.addEventListener('click', event => {
    const target = event.target.closest('[data-page]');
    if (target) {
      event.preventDefault();
      navigate(target.dataset.page);
      return;
    }
    const link = event.target.closest('.prose a[href^="#"]');
    if (link) {
      event.preventDefault();
      if (link.hash !== '#overview') {
        mode = 'full';
        store.set('calculus-mode', mode);
      }
      navigate(link.hash.slice(1));
    }
  });

  function home() {
    const last = pages.find(page => page.id === store.get('calculus-last')) || chapters[0];
    main.innerHTML =
      '<section class="hero"><img class="hero-art" src="阅读资源/calculus-hero.png" alt="" width="1536" height="1024">' +
      '<div class="hero-copy"><div class="eyebrow">THE BEAUTY OF CHANGE</div><h1>在变化中，<br>理解<em>数学。</em></h1>' +
      '<p>从一个极限，到曲线与空间。<br>把公式放回概念，让方法连接知识。</p></div>' +
      '<div class="hero-meta"><span><b>10</b> 个基础章节</span><span><b>' + topics.length + '</b> 篇补充专题</span><span><b>30</b> 道自测题</span></div></section>' +
      '<div class="library-jump"><button data-page="sec-formula">∑ 公式速查</button><button data-page="topic-conditions">定理条件与反例</button><button data-page="sec-practice">自测与解析</button></div>' +
      '<div class="home-tools"><div class="section-label">沿着知识脉络阅读 <small>THE CHAPTERS</small></div><button class="text-btn" data-page="' + last.id + '">' +
      (store.get('calculus-last') ? '继续阅读' : '从第一章开始') + arrow + '</button></div>' +
      '<div class="chapter-grid">' + chapters.map(page =>
        '<button class="chapter-card" data-page="' + page.id + '"><span class="card-number">CHAPTER ' + page.number +
        '</span><span class="card-arrow" aria-hidden="true">↗</span><h2>' + escape(page.title) + '</h2><p>' +
        escape(page.description) + '</p>' + tags(page.tags) + '</button>').join('') + '</div>' +
      '<section class="home-subsection"><div class="section-label">把难点再想深一步 <small>METHODS & INSIGHTS</small></div><div class="topic-grid">' +
      topics.slice(0, 6).map(page =>
        '<button class="topic-card" data-page="' + page.id + '"><small>' + page.number + ' / EXPLORE</small><strong>' +
        escape(page.title) + '</strong><p>' + escape(page.description) + '</p></button>').join('') + '</div></section>' +
      '<section class="practice-banner"><div class="practice-copy"><span class="practice-number">30</span><div><h2>把理解，变成会做。</h2><p>十章分章自测 · 计算、判断与证明 · 解析可折叠</p></div></div><button data-page="sec-practice">开始自测 ↗</button></section>' +
      '<section class="learning-route"><div class="section-label">一条贯穿十章的线索</div><div class="route"><div><strong>极限与局部变化</strong>导数 · 微分 · 近似</div><span class="arrow">→</span><div><strong>累积与无穷表达</strong>积分 · 级数</div><span class="arrow">→</span><div><strong>空间与变化规律</strong>多元微积分 · 微分方程</div></div></section>' +
      '<p class="home-note">先用「精要速查」建立框架，再进入「完整笔记」阅读推导和例题。补充专题与自测题可从左侧目录打开。阅读偏好只保存在当前浏览器。<br><a href="../README.md">Markdown 学习导航 ↗</a> · <a href="../../线性代数/阅读页面/速查笔记.html">线性代数阅读页 ↗</a></p>';
  }

  function wrapExamples(body) {
    const heads = [...body.querySelectorAll('h2,h3,h4')].filter(heading =>
      /完整例题|贯通例题|经典反例|^反例[：:]|^例题[：:]/.test(heading.textContent));
    for (const head of heads) {
      if (head.closest('details')) continue;
      const level = Number(head.tagName[1]);
      const items = [];
      let node = head.nextSibling;
      while (node) {
        if (node.nodeType === 1 && /^H[1-6]$/.test(node.tagName) && Number(node.tagName[1]) <= level) break;
        items.push(node);
        node = node.nextSibling;
      }
      const details = document.createElement('details');
      details.className = 'worked-example';
      const summary = document.createElement('summary');
      summary.textContent = head.textContent.replace(/^(完整例题|贯通例题)[：:]/, '');
      const content = document.createElement('div');
      content.className = 'example-body';
      head.before(details);
      content.append(head, ...items);
      details.append(summary, content);
    }
  }
  function makeToc() {
    tocItems = [...main.querySelectorAll('.prose h2,.prose h3')];
    $('toc').innerHTML = tocItems.map(heading =>
      '<a class="' + (heading.tagName === 'H3' ? 'sub' : '') + '" href="#' + heading.id +
      '" data-anchor="' + heading.id + '">' + heading.innerHTML + '</a>').join('');
    updateProgress();
  }
  function reveal(element) {
    let details = element.closest('details');
    while (details) {
      details.open = true;
      details = details.parentElement.closest('details');
    }
  }
  function gotoHeading(id) {
    const element = document.getElementById(id);
    if (!element) return;
    reveal(element);
    element.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }
  $('toc').addEventListener('click', event => {
    const link = event.target.closest('[data-anchor]');
    if (!link) return;
    event.preventDefault();
    gotoHeading(link.dataset.anchor);
  });

  function showMathNotice() {
    if (current === 'overview' || $('math-notice')) return;
    const notice = document.createElement('p');
    notice.id = 'math-notice';
    notice.className = 'math-notice';
    notice.textContent = '本地公式组件未能加载。请将“阅读资源”文件夹与本页放在一起，再重新打开；原始公式与文字仍可阅读。';
    main.querySelector('.prose')?.before(notice);
  }
  function typeset() {
    if (!window.MathJax?.typesetPromise) return;
    const body = main.querySelector('.prose');
    const token = routeNumber;
    if (!body) return;
    mathQueue = mathQueue.catch(() => {}).then(async () => {
      await MathJax.startup.promise;
      if (token !== routeNumber || !body.isConnected) return;
      await MathJax.typesetPromise([body, $('toc')]);
      updateProgress();
    }).catch(error => {
      console.error('MathJax formula rendering failed:', error);
      mathFailed = true;
      showMathNotice();
    });
  }

  function render() {
    routeNumber++;
    let hash;
    try { hash = decodeURIComponent(location.hash.slice(1)); } catch (_) { hash = ''; }
    const anchor = hash.match(/^((?:sec|topic)-[a-z]+)-(quick|full)-h\d+$/);
    if (anchor) {
      if (current === anchor[1] && mode === (anchor[2] === 'full' ? 'full' : 'summary')) {
        gotoHeading(hash);
        return;
      }
      current = anchor[1];
      mode = anchor[2] === 'full' ? 'full' : 'summary';
    } else {
      current = pages.some(page => page.id === hash) ? hash : 'overview';
    }
    if (window.MathJax?.typesetClear) MathJax.typesetClear([main, $('toc')]);
    const isHome = current === 'overview';
    layout.classList.toggle('home-layout', isHome);
    rail.hidden = isHome;
    tocItems = [];
    $('toc').replaceChildren();
    document.querySelectorAll('.sidebar [data-page]').forEach(button => {
      if (button.dataset.page === current) button.setAttribute('aria-current', 'page');
      else button.removeAttribute('aria-current');
    });
    const page = pages.find(item => item.id === current);
    $('breadcrumb-title').textContent = page?.title || '学习总览';
    document.title = (page?.title || '学习总览') + ' · 高等数学笔记';
    if (isHome) {
      home();
    } else {
      const index = pages.indexOf(page);
      if (page.kind !== 'formula') store.set('calculus-last', page.id);
      const isChapter = page.kind === 'chapter';
      const buttons = isChapter ? '<div class="mode-switch" role="group" aria-label="阅读模式"><button data-mode="summary" aria-pressed="' +
        (mode === 'summary') + '">精要速查</button><button data-mode="full" aria-pressed="' + (mode === 'full') + '">完整笔记</button></div>' : '';
      const eyebrow = isChapter ? 'CHAPTER ' + page.number + ' / 第' + ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十'][index] + '章' :
        page.kind === 'topic' ? 'EXPLORE / 补充理解' : page.kind === 'practice' ? 'PRACTICE / 先思考，再核对' : 'FORMULA INDEX / 常用公式';
      const content = isChapter ? page[mode] : page.full;
      main.innerHTML = '<header class="chapter-header"><div class="eyebrow">' + eyebrow + '</div><h1>' +
        escape(page.title) + '</h1><p>' + escape(page.description) + '</p>' + tags(page.tags) +
        '<div class="chapter-tools">' + buttons + (page.source ? '<a class="source-link" href="' + page.source +
          '">查看 Markdown 原笔记 ↗</a>' : '') + '</div></header><p class="reading-note"><span class="dot"></span>' +
        (isChapter ? mode === 'summary' ? '先理清主线，再进入完整笔记看推导。' : '完整笔记 · 结合例题理解条件与方法。' :
          page.kind === 'practice' ? '先独立作答，再展开该章解析。' : '阅读时同时检查条件、方法与结论。') +
        '</p>' + (page.kind === 'practice' ? '<div class="practice-controls"><button data-solutions="open">展开全部解析</button><button data-solutions="close">收起全部解析</button></div>' : '') +
        '<article class="prose">' + content + '</article><nav class="chapter-footer" aria-label="前后篇目"><button class="page-nav" data-page="' +
        (pages[index - 1]?.id || 'overview') + '"><small>← ' + (index ? '上一篇' : '返回') + '</small>' +
        escape(pages[index - 1]?.title || '学习总览') + '</button><button class="page-nav next" data-page="' +
        (pages[index + 1]?.id || 'overview') + '"><small>' + (index < pages.length - 1 ? '下一篇' : '返回') +
        ' →</small>' + escape(pages[index + 1]?.title || '学习总览') + '</button></nav>';
      if (page.kind !== 'practice' && (!isChapter || mode === 'full')) wrapExamples(main.querySelector('.prose'));
      makeToc();
      typeset();
      if (mathFailed) showMathNotice();
    }
    window.scrollTo({ top: 0, behavior: 'instant' });
    updateProgress();
    if (anchor) requestAnimationFrame(() => gotoHeading(hash));
    if (pendingQuery) {
      const query = pendingQuery.toLowerCase();
      pendingQuery = '';
      requestAnimationFrame(() => {
        const target = [...main.querySelectorAll('.prose h2,.prose h3,.prose h4,.prose p,.prose li')]
          .find(element => element.textContent.toLowerCase().includes(query));
        if (!target) return;
        reveal(target);
        target.scrollIntoView({ block: 'center' });
        target.classList.add('search-hit');
        setTimeout(() => target.classList.remove('search-hit'), 4000);
      });
    }
  }
  main.addEventListener('click', event => {
    const button = event.target.closest('[data-mode]');
    if (button) {
      mode = button.dataset.mode;
      store.set('calculus-mode', mode);
      render();
    }
    const solutions = event.target.closest('[data-solutions]');
    if (solutions) {
      main.querySelectorAll('.prose details').forEach(details => { details.open = solutions.dataset.solutions === 'open'; });
    }
  });

  function updateProgress() {
    const article = main.querySelector('.prose');
    let progress = 0;
    if (article) {
      const top = article.getBoundingClientRect().top + scrollY;
      const available = article.offsetHeight - innerHeight + 110;
      progress = available <= 0 ? 1 : Math.min(1, Math.max(0, (scrollY - top + 110) / available));
    }
    document.documentElement.style.setProperty('--progress', progress);
    $('progress-label').textContent = Math.round(progress * 100) + '%';
    let active = tocItems[0];
    for (const heading of tocItems) {
      if (heading.closest('details:not([open])')) continue;
      if (heading.getBoundingClientRect().top < 170) active = heading;
    }
    $('toc').querySelectorAll('a').forEach(link => link.classList.toggle('active', link.dataset.anchor === active?.id));
  }
  let scheduled = false;
  window.addEventListener('scroll', () => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => { scheduled = false; updateProgress(); });
  }, { passive: true });
  window.addEventListener('resize', updateProgress);
  main.addEventListener('toggle', updateProgress, true);
  $('menu-btn').addEventListener('click', () => {
    const open = !$('sidebar').classList.contains('open');
    $('sidebar').classList.toggle('open', open);
    $('mobile-shade').classList.toggle('show', open);
    $('menu-btn').setAttribute('aria-expanded', String(open));
  });
  $('mobile-shade').addEventListener('click', closeMenu);
  function updateThemeButton() {
    const dark = document.documentElement.dataset.theme === 'dark';
    $('theme-btn').setAttribute('aria-label', dark ? '切换为浅色模式' : '切换为深色模式');
    $('theme-btn').setAttribute('aria-pressed', String(dark));
  }
  updateThemeButton();
  $('theme-btn').addEventListener('click', () => {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = theme;
    store.set('calculus-theme', theme);
    updateThemeButton();
  });
  let printState = [];
  window.addEventListener('beforeprint', () => {
    printState = [...main.querySelectorAll('details')].map(details => [details, details.open]);
    printState.forEach(([details]) => { details.open = true; });
  });
  window.addEventListener('afterprint', () => {
    printState.forEach(([details, open]) => { details.open = open; });
    printState = [];
  });
  $('print-btn').addEventListener('click', () => window.print());

  function search() {
    const value = $('search-input').value.trim().toLowerCase();
    const terms = value.split(/\s+/).filter(Boolean);
    const results = value ? pages.filter(page => terms.every(term =>
      (page.title + ' ' + page.tags.join(' ') + ' ' + page.search).toLowerCase().includes(term)))
      .sort((a, b) => Number(b.title.toLowerCase().includes(value)) - Number(a.title.toLowerCase().includes(value))) : chapters;
    $('search-results').replaceChildren();
    if (!results.length) {
      $('search-results').innerHTML = '<div class="search-empty">没有找到相关内容，试试“可微”“主值”或“收敛”。</div>';
      return;
    }
    results.slice(0, 12).forEach(page => {
      const button = document.createElement('button');
      button.className = 'search-result';
      const strong = document.createElement('strong');
      strong.textContent = page.title + ' · ' + kindLabel[page.kind];
      const description = document.createElement('p');
      const pos = page.search.toLowerCase().indexOf(terms[0]);
      description.textContent = value && pos >= 0 ? page.search.slice(Math.max(0, pos - 18), pos + 95).replace(/\s+/g, ' ') : page.description;
      button.append(strong, description);
      button.addEventListener('click', () => {
        $('search-dialog').close();
        mode = 'full';
        store.set('calculus-mode', mode);
        pendingQuery = $('search-input').value.trim();
        navigate(page.id);
      });
      $('search-results').append(button);
    });
  }
  function openSearch() {
    search();
    $('search-dialog').showModal();
    $('search-input').focus();
  }
  $('search-results').setAttribute('aria-live', 'polite');
  $('search-trigger').addEventListener('click', openSearch);
  $('search-close').addEventListener('click', () => $('search-dialog').close());
  $('search-dialog').addEventListener('close', () => $('search-trigger').focus({ preventScroll: true }));
  $('search-input').addEventListener('input', search);
  $('search-dialog').addEventListener('click', event => { if (event.target === $('search-dialog')) $('search-dialog').close(); });
  document.addEventListener('keydown', event => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      if (!$('search-dialog').open) openSearch();
    }
    if (event.key === 'Escape') {
      const menuOpen = $('sidebar').classList.contains('open');
      closeMenu();
      if (menuOpen) $('menu-btn').focus();
    }
    if ($('search-dialog').open && event.key === 'ArrowDown' && event.target === $('search-input')) {
      event.preventDefault();
      $('search-results').querySelector('button')?.focus();
    }
  });
  window.addEventListener('hashchange', render);
  render();
  const script = document.createElement('script');
  script.src = '阅读资源/tex-svg.js';
  script.async = true;
  script.onload = typeset;
  script.onerror = () => { mathFailed = true; showMathNotice(); };
  document.head.append(script);
})();
