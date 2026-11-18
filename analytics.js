/* Rito0223 방문 통계 (구글 애널리틱스 GA4)
 * 측정 ID는 아래 한 줄만 바꾸면 사이트 전체에 적용돼요.
 * 체류시간·방문자·유입 경로는 GA4가 자동으로 모으고,
 * 아래 이벤트는 문의로 이어지는 클릭을 따로 세기 위한 거예요.
 *   contact_kakao   : 카카오톡 문의 클릭
 *   contact_bunjang : 번개장터 문의·상품 링크 클릭
 *   view_product    : 상품 상세 창 열기
 */
(function () {
  var GA_ID = 'G-XXXXXXXXXX';
  if (!/^G-[A-Z0-9]{4,}$/.test(GA_ID) || GA_ID === 'G-XXXXXXXXXX') return;

  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
  document.head.appendChild(s);

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag('js', new Date());
  gtag('config', GA_ID);

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
    if (href.indexOf('pf.kakao.com') > -1) gtag('event', 'contact_kakao', params);
    else if (href.indexOf('bunjang.co.kr') > -1 || href.indexOf('bgzt.link') > -1) gtag('event', 'contact_bunjang', params);
  }, true);

  function watchDialog() {
    var dlg = document.getElementById('pd');
    if (!dlg || !window.MutationObserver) return;
    new MutationObserver(function () {
      if (!dlg.hasAttribute('open')) return;
      setTimeout(function () {
        var t = document.getElementById('pdTitle');
        gtag('event', 'view_product', { page_type: where(), page_path: location.pathname, product: t ? t.textContent.trim() : '' });
      }, 0);
    }).observe(dlg, { attributes: true, attributeFilter: ['open'] });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', watchDialog);
  else watchDialog();
})();
