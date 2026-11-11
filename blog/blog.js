/* Rito0223 블로그 공통 스크립트: 모바일 메뉴, 문의 말풍선, 하단 문의 바, 목차, 카테고리 필터 */
(function () {
  var $ = function (s) { return document.querySelector(s); };

  /* 모바일 메뉴 */
  var burger = $('#hdBurger'), nav = $('#hdNav');
  var askBtn = $('#askBtn'), askMenu = $('#askMenu');
  function setNav(open) {
    if (!nav) return;
    nav.classList.toggle('open', open);
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    burger.setAttribute('aria-label', open ? '메뉴 닫기' : '메뉴 열기');
  }
  function setAsk(open) {
    if (!askMenu) return;
    askMenu.hidden = !open;
    askBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) {
      if (window.innerWidth <= 760) askMenu.style.top = ($('.hd').getBoundingClientRect().bottom + 8) + 'px';
      else askMenu.style.top = '';
      askMenu.querySelector('a').focus();
    }
  }
  if (burger) burger.addEventListener('click', function () { setAsk(false); setNav(!nav.classList.contains('open')); });
  if (nav) nav.addEventListener('click', function (e) { if (e.target.closest('a')) setNav(false); });
  if (askBtn) askBtn.addEventListener('click', function () { setNav(false); setAsk(askMenu.hidden); });
  document.addEventListener('click', function (e) {
    if (nav && nav.classList.contains('open') && !e.target.closest('.hd')) setNav(false);
    if (askMenu && !askMenu.hidden && !e.target.closest('.ask')) setAsk(false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (askMenu && !askMenu.hidden) { setAsk(false); askBtn.focus(); }
    if (nav && nav.classList.contains('open')) { setNav(false); burger.focus(); }
  });

  /* 모바일 하단 문의 바 + 읽기 진행 막대 */
  var mbar = $('.mbar'), bar = $('.progress'), article = $('.post');
  function onScroll() {
    var y = window.scrollY;
    if (mbar) mbar.classList.toggle('show', y > 320);
    if (bar && article) {
      var r = article.getBoundingClientRect();
      var total = r.height - window.innerHeight;
      var p = total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 0;
      bar.style.transform = 'scaleX(' + p + ')';
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* 목차: 현재 읽는 소제목 강조 */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll('.toc-box a'));
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          tocLinks.forEach(function (a) { a.classList.remove('on'); });
          var a = map[en.target.id];
          if (a) a.classList.add('on');
        }
      });
    }, { rootMargin: '-90px 0px -65% 0px' });
    Object.keys(map).forEach(function (id) { var h = document.getElementById(id); if (h) io.observe(h); });
  }

  /* 블로그 목록: 카테고리 필터 */
  var chips = Array.prototype.slice.call(document.querySelectorAll('.cat-bar button'));
  chips.forEach(function (b) {
    b.addEventListener('click', function () {
      var c = b.getAttribute('data-cat');
      chips.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      document.querySelectorAll('.post-grid li').forEach(function (li) {
        li.hidden = !!c && li.getAttribute('data-cat') !== c;
      });
    });
  });
})();

/* ---------- 상품 카드 → 상품 상세 창 (메인 페이지와 같은 내용) ---------- */
(function () {
  var dlg = document.getElementById('pd'), dataEl = document.getElementById('pd-data');
  if (!dlg || !dataEl) return;
  var P = JSON.parse(dataEl.textContent);
  var el = function (id) { return document.getElementById(id); };
  var CHECK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#C5F25A" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"></path></svg>';
  var cur = null, idx = 0;

  function showImg(i) {
    var imgs = cur.images;
    idx = (i + imgs.length) % imgs.length;
    var img = el('pdImg');
    img.style.visibility = 'visible';
    img.parentNode.classList.add('loading');
    img.src = imgs[idx].src;
    img.alt = imgs[idx].alt;
    if (img.complete && img.naturalWidth) img.parentNode.classList.remove('loading');
    el('pdCount').textContent = (idx + 1) + ' / ' + imgs.length;
    Array.prototype.forEach.call(el('pdThumbs').children, function (b, j) { b.setAttribute('aria-current', j === idx ? 'true' : 'false'); });
  }
  el('pdImg').addEventListener('error', function () { this.style.visibility = 'hidden'; this.parentNode.classList.remove('loading'); });
  el('pdImg').addEventListener('load', function () { this.parentNode.classList.remove('loading'); });
  el('pdPrev').addEventListener('click', function () { showImg(idx - 1); });
  el('pdNext').addEventListener('click', function () { showImg(idx + 1); });

  function open(key) {
    cur = P[key];
    if (!cur) return false;
    el('pdTitle').textContent = cur.title;
    el('pdPrice').innerHTML = '';
    var b = document.createElement('b'); b.textContent = cur.price; el('pdPrice').appendChild(b);
    var s = document.createElement('span'); s.textContent = cur.note; el('pdPrice').appendChild(s);
    el('pdDesc').textContent = cur.desc;
    el('pdTags').innerHTML = (cur.tags || []).map(function (t) { return (P._tags || {})[t] || ''; }).join('');
    var thumbs = el('pdThumbs');
    thumbs.innerHTML = '';
    cur.images.forEach(function (im, j) {
      var tb = document.createElement('button');
      tb.type = 'button';
      tb.setAttribute('aria-label', (j + 1) + '번째 사진 보기');
      var ti = document.createElement('img'); ti.src = im.src; ti.alt = ''; ti.loading = 'lazy';
      tb.appendChild(ti);
      tb.addEventListener('click', function () { showImg(j); });
      thumbs.appendChild(tb);
    });
    thumbs.hidden = cur.images.length < 2;
    el('pdPrev').hidden = el('pdNext').hidden = cur.images.length < 2;
    showImg(0);
    var ul = el('pdList');
    ul.innerHTML = '';
    cur.list.forEach(function (it) {
      var li = document.createElement('li');
      li.innerHTML = CHECK;
      var sp = document.createElement('span');
      sp.textContent = typeof it === 'string' ? it : it.t;
      li.appendChild(sp);
      ul.appendChild(li);
    });
    el('pdBunjang').href = cur.bunjang;
    el('pdBunjang').textContent = '번개장터 문의';
    var more = el('pdMore');
    if (cur.more) { more.href = cur.more; more.hidden = false; } else { more.hidden = true; }
    if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
    el('pdClose').focus();
    return true;
  }
  function close() { if (dlg.open) dlg.close(); else dlg.removeAttribute('open'); }

  el('pdClose').addEventListener('click', close);
  dlg.addEventListener('click', function (e) { if (e.target === dlg) close(); });
  document.querySelectorAll('.pd-actions a, .pd-more').forEach(function (a) { a.target = '_blank'; a.rel = 'noopener'; });
  document.querySelectorAll('[data-product]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      if (open(a.getAttribute('data-product'))) e.preventDefault();
    });
  });
})();
