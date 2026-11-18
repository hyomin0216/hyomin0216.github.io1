/* Rito0223 방문 통계 (구글 태그 / 구글 애널리틱스)
 * 태그 ID는 아래 한 줄만 바꾸면 사이트 전체에 적용돼요.
 * 체류시간·방문자·유입 경로는 구글 애널리틱스가 자동으로 모으고,
 * 아래 이벤트는 문의로 이어지는 클릭을 따로 세기 위한 거예요.
 *   contact_kakao   : 카카오톡 문의 클릭
 *   contact_bunjang : 번개장터 문의·상품 링크 클릭
 *   view_product    : 상품 상세 창 열기
 */
(function () {
  var TAG_ID = 'GTM-KLNN53SW';
  if (!/^(GTM|G)-[A-Z0-9]{4,}$/.test(TAG_ID)) return;

  // 구글 태그 설치 코드 (구글이 안내한 코드와 같은 내용)
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag('js', new Date());
  var s = document.createElement('script');
  s.async = true;
  s.src = TAG_ID.indexOf('GTM-') === 0
    ? 'https://www.googletagmanager.com/gtm.js?id=' + TAG_ID
    : 'https://www.googletagmanager.com/gtag/js?id=' + TAG_ID;
  (document.head || document.documentElement).appendChild(s);
  if (TAG_ID.indexOf('G-') === 0) gtag('config', TAG_ID);

  // 이벤트 보내기: 구글 태그(gtag)와 태그 관리자 트리거(dataLayer) 둘 다에서 쓸 수 있게
  function track(name, params) {
    gtag('event', name, params);
    var o = { event: 'rito_' + name };
    for (var k in params) o[k] = params[k];
    window.dataLayer.push(o);
  }

  function where() {
    var p = location.pathname;
    if (p === '/' || p === '/index.html') return 'home';
    if (p.indexOf('/blog/') === 0) return p === '/blog/' ? 'blog_list' : 'blog_post';
    return 'service_page';
  }
  function productName(el) {
    var t = document.getElementById('pdTitle');
    var dlg = el.closest && el.closest('dialog');
    if (dlg && t && t.textContent) return t.textContent.trim();
    return '';
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var params = { page_type: where(), page_path: location.pathname, link_text: (a.innerText || a.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60) };
    var prod = productName(a);
    if (prod) params.product = prod;
    if (href.indexOf('pf.kakao.com') > -1) track('contact_kakao', params);
    else if (href.indexOf('bunjang.co.kr') > -1 || href.indexOf('bgzt.link') > -1) track('contact_bunjang', params);
  }, true);

  function watchDialog() {
    var dlg = document.getElementById('pd');
    if (!dlg || !window.MutationObserver) return;
    new MutationObserver(function () {
      if (!dlg.hasAttribute('open')) return;
      setTimeout(function () {
        var t = document.getElementById('pdTitle');
        track('view_product', { page_type: where(), page_path: location.pathname, product: t ? t.textContent.trim() : '' });
      }, 0);
    }).observe(dlg, { attributes: true, attributeFilter: ['open'] });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', watchDialog);
  else watchDialog();
})();
