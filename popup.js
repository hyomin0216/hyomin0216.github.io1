/* Rito0223 첫 방문 팝업
 * 바꾸는 곳은 아래 설정 세 줄뿐이에요.
 *   IMAGE   : 세로 이미지 주소 (권장 1080×1350). 비워 두면 팝업이 뜨지 않아요.
 *   LINK    : 이미지를 눌렀을 때 갈 주소. 비워 두면 눌러도 이동하지 않아요.
 *   VERSION : 이미지를 새로 바꿀 때 숫자를 올리면 '다시 보지 않기'를 눌렀던 사람에게도 새 팝업이 한 번 떠요.
 * 동작
 *   - 사이트에 처음 들어온 페이지에서만 떠요. 같은 방문 중 다른 페이지로 가면 안 떠요.
 *   - 닫기: 이번 방문에서만 닫혀요. 다음에 새로 들어오면 다시 떠요.
 *   - 다시 보지 않기: 이 기기에서는 같은 팝업이 다시 안 떠요.
 */
(function () {
  var IMAGE = '/images/popup/notice-20261122.png';
  var LINK = '';
  var VERSION = '20261122';
  var ALT = '안내사항: 번개장터 상점 일시 이용 제한 안내, 카카오톡 구매·문의는 정상 운영';
  var W = 879, H = 1119;   // 이미지 가로·세로 픽셀 (비율을 맞추는 데 써요)

  if (!IMAGE) return;
  var SEEN = 'rito_popup_seen', NEVER = 'rito_popup_never';
  function get(store, k) { try { return window[store].getItem(k); } catch (e) { return null; } }
  function set(store, k, v) { try { window[store].setItem(k, v); } catch (e) {} }

  if (get('localStorage', NEVER) === VERSION) return;   // 다시 보지 않기
  if (get('sessionStorage', SEEN)) return;              // 이번 방문에서 이미 한 번 뜸
  set('sessionStorage', SEEN, '1');                     // 첫 페이지에서만 뜨게 표시

  var css = '' +
    '.rp-dim{position:fixed;inset:0;z-index:2147483000;background:rgba(0,0,0,.66);display:flex;align-items:center;justify-content:center;padding:20px;animation:rpIn .25s ease-out}' +
    '.rp-pop{position:relative;width:min(420px,100%);border-radius:16px;overflow:hidden;background:#141414;border:1px solid #2A2A2A;box-shadow:0 24px 60px rgba(0,0,0,.6);animation:rpUp .3s ease-out;font-family:"Plus Jakarta Sans","Noto Sans KR",system-ui,sans-serif}' +
    '.rp-img{display:block;width:100%;background:#000}' +
    '.rp-img img{display:block;width:100%;height:auto;max-height:calc(100vh - 120px);max-height:calc(100dvh - 120px);object-fit:contain}' +
    '.rp-x{position:absolute;top:10px;right:10px;width:36px;height:36px;border-radius:50%;border:0;background:rgba(0,0,0,.6);color:#fff;font-size:20px;line-height:1;cursor:pointer}' +
    '.rp-bar{display:flex;border-top:1px solid #2A2A2A}' +
    '.rp-bar button{flex:1;min-height:52px;font:inherit;font-size:14.5px;background:none;border:0;color:#A3A3A3;cursor:pointer}' +
    '.rp-bar button+button{border-left:1px solid #2A2A2A;color:#EDEDED;font-weight:700}' +
    '.rp-bar button:hover{background:#1C1C1C}' +
    '.rp-pop button:focus-visible{outline:2px solid #EDEDED;outline-offset:-2px}' +
    '@keyframes rpIn{from{opacity:0}to{opacity:1}}@keyframes rpUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}' +
    '@media (prefers-reduced-motion:reduce){.rp-dim,.rp-pop{animation:none}}';

  function show() {
    var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    var dim = document.createElement('div');
    dim.className = 'rp-dim';
    dim.setAttribute('role', 'dialog');
    dim.setAttribute('aria-modal', 'true');
    dim.setAttribute('aria-label', ALT);
    var tag = LINK ? 'a' : 'div';
    dim.innerHTML = '<div class="rp-pop">' +
      '<' + tag + ' class="rp-img"' + (LINK ? ' href="' + LINK + '"' + (/^https?:/.test(LINK) ? ' target="_blank" rel="noopener"' : '') : '') + '>' +
      '<img src="' + IMAGE + '" alt="' + ALT + '" width="' + W + '" height="' + H + '"></' + tag + '>' +
      '<button type="button" class="rp-x" aria-label="닫기">×</button>' +
      '<div class="rp-bar"><button type="button" class="rp-never">다시 보지 않기</button><button type="button" class="rp-close">닫기</button></div></div>';
    var prevOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = 'hidden';
    function close() {
      document.documentElement.style.overflow = prevOverflow;
      dim.remove();
      document.removeEventListener('keydown', onKey);
    }
    function onKey(e) { if (e.key === 'Escape') close(); }
    dim.querySelector('.rp-close').addEventListener('click', close);
    dim.querySelector('.rp-x').addEventListener('click', close);
    dim.querySelector('.rp-never').addEventListener('click', function () { set('localStorage', NEVER, VERSION); close(); });
    dim.addEventListener('click', function (e) { if (e.target === dim) close(); });
    document.addEventListener('keydown', onKey);
    var img = dim.querySelector('img');
    img.addEventListener('error', close);   // 이미지가 없으면 빈 팝업 대신 그냥 닫기
    if (LINK && window.gtag) dim.querySelector('.rp-img').addEventListener('click', function () { window.gtag('event', 'popup_click', { page_path: location.pathname }); });
    document.body.appendChild(dim);
    dim.querySelector('.rp-close').focus({ preventScroll: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', show);
  else show();
})();
