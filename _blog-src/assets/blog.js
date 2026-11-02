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
