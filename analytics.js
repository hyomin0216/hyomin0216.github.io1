/* Rito0223 방문 통계 (구글 애널리틱스 + 구글 태그 관리자)
 * ID는 아래 두 줄만 바꾸면 사이트 전체에 적용돼요.
 * 체류시간·방문자·유입 경로는 구글 애널리틱스가 자동으로 모으고,
 * 아래 이벤트는 문의로 이어지는 클릭을 따로 세기 위한 거예요.
 *   contact_kakao   : 카카오톡 문의 클릭
 *   contact_bunjang : 번개장터 문의·상품 링크 클릭
 *   view_product    : 상품 상세 창 열기
 */
(function () {
  var GA_ID = 'G-JPZ2M8BPFM';   // 구글 애널리틱스 측정 ID (체류시간·방문자)
  var GTM_ID = 'GTM-KLNN53SW';  // 구글 태그 관리자 컨테이너 (나중에 다른 태그 추가용)
  // 주의: 태그 관리자 안에 같은 GA4 태그(G-JPZ2M8BPFM)를 또 넣으면 방문이 두 번씩 잡혀요.

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag('js', new Date());
  function load(src) {
    var s = document.createElement('script');
    s.async = true;
    s.src = src;
    (document.head || document.documentElement).appendChild(s);
  }
  if (/^G-[A-Z0-9]{4,}$/.test(GA_ID)) {
    load('https://www.googletagmanager.com/gtag/js?id=' + GA_ID);
    gtag('config', GA_ID);
  }
  if (/^GTM-[A-Z0-9]{4,}$/.test(GTM_ID)) {
    window.dataLayer.push({ 'gtm.start': new Date().getTime(), event: 'gtm.js' });
    load('https://www.googletagmanager.com/gtm.js?id=' + GTM_ID);
  }

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
