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

  /* 블로그 목록: 검색 + 카테고리 필터 + 페이지 나누기 */
  var grid = $('#postGrid');
  if (grid) {
    var PER = 9;
    var lis = Array.prototype.slice.call(grid.children);
    var chips = Array.prototype.slice.call(document.querySelectorAll('.cat-bar button'));
    var input = $('#blSearch'), feat = $('#feat'), pager = $('#pager');
    var catLabel = $('#archCat'), count = $('#archCount'), empty = $('#blEmpty');
    var st = { cat: '', q: '', page: 1 };
    var CL = '<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 6-6 6 6 6"></path></svg>';

    function btn(label, page, opts) {
      var b = document.createElement('button');
      b.type = 'button'; b.innerHTML = label;
      if (opts && opts.cur) b.setAttribute('aria-current', 'page');
      if (opts && opts.dis) b.disabled = true;
      if (opts && opts.aria) b.setAttribute('aria-label', opts.aria);
      b.addEventListener('click', function () {
        st.page = page; render();
        var top = $('.archive').getBoundingClientRect().top + window.scrollY - 90;
        window.scrollTo({ top: top, behavior: 'smooth' });
      });
      return b;
    }
    function render() {
      var q = st.q.trim().toLowerCase(), filtering = !!(st.cat || q);
      var match = lis.filter(function (li) {
        if (!filtering && li.hasAttribute('data-feat')) return false;
        if (st.cat && li.getAttribute('data-cat') !== st.cat) return false;
        if (q && li.getAttribute('data-q').indexOf(q) < 0) return false;
        return true;
      });
      var pages = Math.max(1, Math.ceil(match.length / PER));
      if (st.page > pages) st.page = pages;
      var from = (st.page - 1) * PER, show = match.slice(from, from + PER);
      lis.forEach(function (li) { li.hidden = show.indexOf(li) < 0; });
      if (feat) feat.hidden = filtering;
      var total = filtering ? match.length : match.length + 1;
      if (catLabel) catLabel.textContent = st.cat || (q ? '검색 결과' : '전체 카테고리');
      if (count) count.textContent = '총 ' + total + '개 가이드';
      if (empty) empty.hidden = match.length > 0;
      pager.innerHTML = '';
      if (pages < 2) return;
      pager.appendChild(btn(CL, st.page - 1, { dis: st.page === 1, aria: '이전 페이지' }));
      for (var i = 1; i <= pages; i++) {
        if (pages > 7 && i > 1 && i < pages && Math.abs(i - st.page) > 1) {
          if (i === 2 || i === pages - 1) { var g = document.createElement('span'); g.className = 'gap'; g.textContent = '...'; pager.appendChild(g); }
          continue;
        }
        pager.appendChild(btn(String(i), i, { cur: i === st.page }));
      }
      pager.appendChild(btn('다음', st.page + 1, { dis: st.page === pages, aria: '다음 페이지' }));
    }
    chips.forEach(function (b) {
      b.addEventListener('click', function () {
        st.cat = b.getAttribute('data-cat'); st.page = 1;
        chips.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        render();
      });
    });
    if (input) input.addEventListener('input', function () { st.q = input.value; st.page = 1; render(); });
    render();
  }
})();

/* ---------- 상품 카드 → 상품 상세 창 (메인 페이지와 같은 내용) ---------- */
(function () {
  var dlg = document.getElementById('pd'), dataEl = document.getElementById('pd-data');
  if (!dlg || !dataEl) return;
  var P = JSON.parse(dataEl.textContent);
  var el = function (id) { return document.getElementById(id); };
  var CHECK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"></path></svg>';
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
