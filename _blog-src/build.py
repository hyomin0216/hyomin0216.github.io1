#!/usr/bin/env python3
"""
Rito0223 블로그 빌드 스크립트

사용법 (사이트 루트에서):
    python3 _blog-src/build.py

_blog-src/posts/ 안의 글 파일(.json, 파일 하나 = 글 하나)을 읽어서 아래 파일을 다시 만듭니다.
  - blog/<slug>/index.html  (글 페이지)
  - blog/index.html         (글 목록)
  - blog/feed.xml           (RSS)
  - blog/blog.css, blog/blog.js
  - sitemap.xml, llms.txt, robots.txt

새 글 쓰는 법: _blog-src/posts/_template.json 을 복사해서 이름을 바꾸고 내용을 채우면 됩니다.
(이름이 _ 로 시작하는 파일과 "draft": true 인 글은 공개하지 않아요)
"""
import html
import json
import math
import os
import re
import shutil
import sys
from datetime import datetime
from email.utils import format_datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from seo_common import (SITE, KAKAO, BUNJANG_SHOP, OG_IMAGE, ORG, faq_schema, ld_json, head_meta)

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(HERE)
POSTS_DIR = os.path.join(HERE, "posts")
KST = ZoneInfo("Asia/Seoul")
HOME_MODIFIED = "2026-10-26"   # 메인 페이지를 고치면 이 날짜도 바꿔 주세요
SERVICE_MODIFIED = "2026-10-05"
esc = html.escape

# ---------------------------------------------------------------- 글 읽기
def slug_id(text):
    t = re.sub(r"<[^>]+>", "", text)
    t = re.sub(r"[^\w가-힣\s-]", "", t).strip()
    return re.sub(r"\s+", "-", t)


INLINE_CODE = re.compile(r"`([^`]+)`")
INLINE_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
INLINE_BOLD = re.compile(r"\*\*(.+?)\*\*")


def md(text):
    """글 안의 간단한 표기를 HTML로: **굵게**, [링크 글자](주소), `코드`"""
    t = esc(str(text), quote=False)
    codes = []
    t = INLINE_CODE.sub(lambda m: codes.append(m.group(1)) or f"\x00{len(codes) - 1}\x00", t)

    def link(m):
        label, url = m.group(1), m.group(2)
        ext = url.startswith("http") and "rito0223.com" not in url
        tgt = ' target="_blank" rel="noopener"' if ext else ""
        return f'<a href="{url}"{tgt}>{label}</a>'

    t = INLINE_LINK.sub(link, t)
    t = INLINE_BOLD.sub(r"<strong>\1</strong>", t)
    return re.sub("\x00(\\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", t)


def render_blocks(blocks, where):
    out = []
    for i, b in enumerate(blocks, 1):
        if isinstance(b, str):
            b = {"p": b}
        if not isinstance(b, dict) or len(b) != 1:
            sys.exit(f"[오류] {where}: content {i}번째 블록 모양이 이상해요 → {json.dumps(b, ensure_ascii=False)[:80]}")
        kind, val = next(iter(b.items()))
        if kind in ("h2", "h3", "p"):
            out.append(f"<{kind}>{md(val)}</{kind}>")
        elif kind in ("ul", "ol"):
            out.append(f"<{kind}>" + "".join(f"<li>{md(x)}</li>" for x in val) + f"</{kind}>")
        elif kind == "quote":
            out.append(f"<blockquote><p>{md(val)}</p></blockquote>")
        elif kind == "table":
            head = "".join(f"<th>{md(h)}</th>" for h in val.get("head", []))
            rows = "".join("<tr>" + "".join(f"<td>{md(c)}</td>" for c in r) + "</tr>" for r in val.get("rows", []))
            out.append(f"<table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>")
        elif kind == "img":
            cap = f"<figcaption>{md(val['caption'])}</figcaption>" if val.get("caption") else ""
            out.append(f'<figure><img src="{esc(val["src"])}" alt="{esc(val.get("alt", ""))}" loading="lazy" decoding="async">{cap}</figure>')
        elif kind == "html":
            out.append(str(val))
        else:
            sys.exit(f"[오류] {where}: content {i}번째 블록 종류 '{kind}'는 쓸 수 없어요 (h2, h3, p, ul, ol, quote, table, img, html)")
    return "\n".join(out)


REQUIRED = ("slug", "title", "description", "category", "date", "content")


def load_posts():
    posts = []
    for name in sorted(os.listdir(POSTS_DIR)):
        if not name.endswith(".json") or name.startswith("_"):
            continue
        path = os.path.join(POSTS_DIR, name)
        try:
            meta = json.load(open(path, encoding="utf-8"))
        except json.JSONDecodeError as e:
            sys.exit(f"[오류] {name}: JSON 형식이 틀렸어요 ({e.lineno}번째 줄 {e.colno}번째 칸 근처). 쉼표·따옴표를 확인해 주세요.")
        for k in REQUIRED:
            if not meta.get(k):
                sys.exit(f"[오류] {name}: '{k}' 값이 비어 있어요")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", meta["slug"]):
            sys.exit(f"[오류] {name}: slug는 영문 소문자·숫자·하이픈(-)만 쓸 수 있어요 → {meta['slug']}")
        for k in ("date", "updated"):
            if meta.get(k) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta[k]):
                sys.exit(f"[오류] {name}: {k}는 2026-10-26 같은 형식이어야 해요 → {meta[k]}")
        if meta.get("draft"):
            print("  건너뜀(초안):", name)
            continue
        meta.setdefault("updated", meta["date"])
        meta.setdefault("tldr", [])
        meta.setdefault("keywords", "")
        meta.setdefault("cta", "server")
        meta["faq"] = [(f["q"], f["a"]) if isinstance(f, dict) else tuple(f) for f in meta.get("faq", [])]
        meta["sources"] = [(s["name"], s["url"]) if isinstance(s, dict) else tuple(s) for s in meta.get("sources", [])]
        meta["tldr"] = [md(t) for t in meta["tldr"]]
        body = render_blocks(meta["content"], name)
        toc, seen = [], set()

        def add_id(mh):
            attrs, inner = mh.group(1), mh.group(2)
            hid = slug_id(inner) or f"s{len(toc) + 1}"
            while hid in seen:
                hid += "-2"
            seen.add(hid)
            toc.append((hid, re.sub(r"<[^>]+>", "", inner)))
            return f'<h2 id="{hid}"{attrs}>{inner}</h2>'

        body = re.sub(r"<h2([^>]*)>(.*?)</h2>", add_id, body, flags=re.S)
        body = re.sub(r"<table>", '<div class="tbl"><table>', body)
        body = re.sub(r"</table>", "</table></div>", body)
        text_len = len(re.sub(r"<[^>]+>|\s", "", body))
        meta.update(body=body, toc=toc, minutes=max(2, math.ceil(text_len / 500)), chars=text_len)
        posts.append(meta)
    if not posts:
        sys.exit("[오류] 공개할 글이 없어요")
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts


def iso(d):
    return f"{d}T00:00:00+09:00"


def kdate(d):
    y, m, dd = d.split("-")
    return f"{int(y)}년 {int(m)}월 {int(dd)}일"


def dot(d):
    return d.replace("-", ".")

# ---------------------------------------------------------------- 공통 조각
ICON_KAKAO = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"></path></svg>'


def header(blog_active=True):
    cur = ' aria-current="page"' if blog_active else ""
    return f'''<a class="skip" href="#main">본문 바로가기</a>
<header class="hd">
<div class="hd-in">
<a class="brand" href="/" aria-label="Rito0223 홈"><span class="brand-logo"><img src="/logo-sm.png" alt="Rito0223" width="91" height="57" onerror="this.parentNode.outerHTML='<span class=&quot;brand-txt&quot;>Rito0223</span>'"></span></a>
<nav class="hd-nav" id="hdNav" aria-label="주요 메뉴">
<a href="/#products">상품</a>
<a href="/#guide">부스트 가이드</a>
<a href="/#why">진행 방식</a>
<a href="/#faq">자주 묻는 질문</a>
<a href="/blog/"{cur}>블로그</a>
</nav>
<div class="hd-right">
<div class="ask">
<button type="button" id="askBtn" aria-expanded="false" aria-controls="askMenu">문의하기<svg class="ask-chev" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"></path></svg></button>
<div class="ask-menu" id="askMenu" role="menu" aria-label="문의 방법" hidden>
<p class="ask-title">어디로 문의할까요?</p>
<a role="menuitem" class="ask-item" href="{KAKAO}" target="_blank" rel="noopener"><span class="ask-ico" style="background:#FEE500;color:#191919;">{ICON_KAKAO}</span><span class="ask-txt"><b>카카오톡 문의</b><small>1:1 채팅으로 바로 상담</small></span><svg class="ask-go" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 6 6 6-6 6"></path></svg></a>
<a role="menuitem" class="ask-item" href="{BUNJANG_SHOP}" target="_blank" rel="noopener"><span class="ask-ico" style="background:#2B2D3C;color:#FFFFFF;"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M13 2 4 14h7l-1 8 9-12h-7z"></path></svg></span><span class="ask-txt"><b>번개장터 문의</b><small>Rito0223 상점 바로가기</small></span><svg class="ask-go" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 6 6 6-6 6"></path></svg></a>
</div>
</div>
<button type="button" class="hd-burger" id="hdBurger" aria-controls="hdNav" aria-expanded="false" aria-label="메뉴 열기"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path class="hb1" d="M4 7h16"></path><path class="hb2" d="M4 12h16"></path><path class="hb3" d="M4 17h16"></path></svg></button>
</div>
</div>
</header>'''


FOOTER = f'''<footer class="ft">
<div class="ft-in">
<span class="ft-brand"><img src="/logo-sm.png" alt="" width="48" height="30" onerror="this.style.display='none'"><span><b>rito<span>0223</span></b> — 디스코드 서버제작 · 니트로 · 부스트</span></span>
<nav aria-label="푸터 메뉴"><a href="/discord-server-creation/">서버제작</a><a href="/discord-nitro/">니트로</a><a href="/discord-server-boost/">서버부스트</a><a href="/blog/">블로그</a></nav>
<span>© 2026 Rito0223</span>
</div>
</footer>
<div class="mbar" role="region" aria-label="빠른 문의">
<a class="mbar-kakao" href="{KAKAO}" target="_blank" rel="noopener">{ICON_KAKAO}카카오톡 문의</a>
<a class="mbar-bj" href="{BUNJANG_SHOP}" target="_blank" rel="noopener">번개장터 상점</a>
</div>
<script src="/blog/blog.js" defer></script>'''

CTAS = {
    "server": ("서버 세팅, 직접 하기 번거롭다면", "채널·역할·권한·봇·디자인까지 목적에 맞게 완성해 드려요. 일반 4,000원부터, 프리미엄 10,000원.", "/discord-server-creation/", "디스코드 서버제작 자세히 보기"),
    "premium": ("테러 방지·채널 꾸미기까지 한 번에", "프리미엄 서버제작은 1시간 이내 출고, 모든 봇 세팅, 테러 방지봇과 행동 로그, 이모지·특수문자 채널 꾸미기까지 포함해요. 10,000원.", "/#products", "프리미엄 서버제작 보기"),
    "boost": ("원하는 레벨까지 바로 맞추고 싶다면", "목표 레벨(1·2·3)만 알려주세요. 필요한 부스트 개수와 함께 안내해 드려요. 로켓지급이면 1시간 안에 받아요.", "/discord-server-boost/", "서버부스트 레벨별 안내 보기"),
    "nitro": ("니트로, 출처가 확실한 곳에서", "원하는 종류(니트로 / 니트로 베이직)와 기간을 알려주시면 1:1 상담 후 안전하게 진행해요. 번개장터 누적 판매 450건·후기 300건 이상.", "/discord-nitro/", "니트로 종류 비교 보기"),
}

FAQ_ICO = '<svg class="faq-ico" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14"></path><path d="M5 12h14"></path></svg>'


def page(head, body):
    return f'''<!doctype html>
<html lang="ko">
<head>
{head}
</head>
<body>
<div id="pageLoader" class="pl" role="status" aria-live="polite">
<div class="pl-box"><img src="https://www.rito0223.com/logo-sm.png" alt="" width="77" height="48"><span class="pl-ring" aria-hidden="true"></span><p>불러오는 중…</p></div>
</div>
<script>
(function () {{
  var el = document.getElementById('pageLoader'), done = false;
  var t = setTimeout(function () {{ if (!done) el.classList.add('show'); }}, 350);
  function hide() {{
    if (done) return; done = true; clearTimeout(t);
    el.classList.add('hide');
    setTimeout(function () {{ if (el.parentNode) el.parentNode.removeChild(el); }}, 400);
  }}
  if (document.readyState === 'complete') hide();
  else {{ window.addEventListener('load', hide); setTimeout(hide, 8000); }}
}})();
</script>
{body}
</body>
</html>
'''


def breadcrumb(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

# ---------------------------------------------------------------- 글 페이지
def render_post(p, posts):
    url = f"{SITE}/blog/{p['slug']}/"
    title = f"{p['title']} | Rito0223"
    extra = (f'<meta property="article:published_time" content="{iso(p["date"])}">\n'
             f'<meta property="article:modified_time" content="{iso(p["updated"])}">\n'
             f'<meta property="article:section" content="{esc(p["category"])}">\n')
    if p["keywords"]:
        extra = f'<meta name="keywords" content="{esc(p["keywords"])}">\n' + extra
    graph = [
        {"@type": "BlogPosting", "@id": url + "#article", "headline": p["title"], "description": p["description"],
         "image": OG_IMAGE, "url": url, "mainEntityOfPage": url,
         "datePublished": iso(p["date"]), "dateModified": iso(p["updated"]), "inLanguage": "ko-KR",
         "articleSection": p["category"], "keywords": p["keywords"], "wordCount": p["chars"],
         "author": {"@id": SITE + "/#org"}, "publisher": {"@id": SITE + "/#org"},
         "isPartOf": {"@id": SITE + "/blog/#blog"},
         "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".post h1", ".tldr"]}},
        ORG,
        breadcrumb([("홈", SITE + "/"), ("블로그", SITE + "/blog/"), (p["title"], url)]),
    ]
    if p["faq"]:
        graph.append(faq_schema(url, p["faq"]))
    head = (head_meta(esc(title), esc(p["description"]), url, og_type="article", extra=extra)
            + '\n<link rel="stylesheet" href="/blog/blog.css">\n' + ld_json(graph))

    tldr = ""
    if p["tldr"]:
        tldr = ('<aside class="tldr" aria-label="핵심 요약"><p class="tldr-h">핵심 요약</p><ul>'
                + "".join(f"<li>{t}</li>" for t in p["tldr"]) + "</ul></aside>")
    faq = ""
    if p["faq"]:
        faq = ('<section class="post-section" id="faq" aria-labelledby="faq-h"><h2 id="faq-h">자주 묻는 질문</h2>'
               + "".join(f'<details class="faq-item"><summary><span>{esc(q)}</span>{FAQ_ICO}</summary><p>{esc(a)}</p></details>' for q, a in p["faq"])
               + "</section>")
    sources = ""
    if p["sources"]:
        sources = ('<div class="sources">참고 자료<ul>'
                   + "".join(f'<li><a href="{esc(u)}" target="_blank" rel="noopener">{esc(n)}</a></li>' for n, u in p["sources"])
                   + "</ul>세부 수치는 디스코드 정책에 따라 바뀔 수 있어요.</div>")
    ct, cd, cu, cl = CTAS.get(p["cta"], CTAS["server"])
    cta = f'''<div class="cta-card"><h2>{ct}</h2><p>{cd}</p><div class="cta-btns"><a class="btn btn-kakao" href="{KAKAO}" target="_blank" rel="noopener">{ICON_KAKAO}카카오톡 문의</a><a class="btn btn-line" href="{cu}">{cl}</a></div></div>'''
    others = [o for o in posts if o["slug"] != p["slug"]]
    rel = [o for o in others if o["category"] == p["category"]] + [o for o in others if o["category"] != p["category"]]
    related = ('<section class="post-section" aria-labelledby="rel-h"><h2 id="rel-h">함께 보면 좋은 글</h2><div class="related">'
               + "".join(f'<a href="/blog/{o["slug"]}/">{esc(o["title"])}<small>{esc(o["category"])} · {dot(o["date"])}</small></a>' for o in rel[:2])
               + "</div></section>") if rel else ""
    updated = f' · <span>{kdate(p["updated"])} 수정</span>' if p["updated"] != p["date"] else ""
    toc_items = p["toc"] + ([("faq", "자주 묻는 질문")] if p["faq"] else [])
    toc = "".join(f'<li><a href="#{hid}">{esc(t)}</a></li>' for hid, t in toc_items)

    body = f'''<div class="progress" aria-hidden="true"></div>
{header()}
<main id="main">
<div class="bl-wrap">
<div class="post-layout">
<article class="post">
<nav class="crumb" aria-label="현재 위치"><a href="/">홈</a><span aria-hidden="true">›</span><a href="/blog/">블로그</a><span aria-hidden="true">›</span><span>{esc(p["category"])}</span></nav>
<span class="chip">{esc(p["category"])}</span>
<h1>{esc(p["title"])}</h1>
<p class="lead">{esc(p["description"])}</p>
<p class="meta"><time datetime="{iso(p["date"])}">{kdate(p["date"])}</time> 작성{updated}<span>· 약 {p["minutes"]}분</span><span>· Rito0223</span></p>
{tldr}
<div class="post-body">
{p["body"]}
</div>
{faq}
{sources}
{cta}
{related}
<a class="back" href="/blog/">← 블로그 전체 글 보기</a>
</article>
<aside class="toc" aria-label="목차">
<div class="toc-in">
<nav class="toc-box"><p>CONTENTS</p><ol>{toc}</ol></nav>
<div class="toc-cta"><b>직접 하기 번거롭다면</b><span>서버제작·니트로·부스트, 카톡 한 번이면 끝나요.</span><a class="btn btn-kakao" href="{KAKAO}" target="_blank" rel="noopener">{ICON_KAKAO}카카오톡 문의</a></div>
</div>
</aside>
</div>
</div>
</main>
{FOOTER}'''
    return page(head, body)

# ---------------------------------------------------------------- 목록 페이지
def render_index(posts):
    url = SITE + "/blog/"
    title = "디스코드 가이드 블로그 | Rito0223"
    desc = "디스코드 서버 만드는 법, 채널 꾸미기, 서버부스트, 니트로, 테러·사기 예방까지. 디스코드를 더 잘 쓰기 위한 정보를 정리합니다."
    graph = [
        {"@type": "Blog", "@id": url + "#blog", "name": "Rito0223 디스코드 가이드 블로그", "description": desc, "url": url,
         "inLanguage": "ko-KR", "publisher": {"@id": SITE + "/#org"},
         "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/blog/{p['slug']}/",
                       "datePublished": iso(p["date"]), "dateModified": iso(p["updated"])} for p in posts]},
        ORG,
        breadcrumb([("홈", SITE + "/"), ("블로그", url)]),
    ]
    head = head_meta(esc(title), esc(desc), url) + '\n<link rel="stylesheet" href="/blog/blog.css">\n' + ld_json(graph)
    cats = []
    for p in posts:
        if p["category"] not in cats:
            cats.append(p["category"])
    chips = '<button type="button" data-cat="" aria-pressed="true">전체</button>' + "".join(
        f'<button type="button" data-cat="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in cats)
    items = []
    for i, p in enumerate(posts):
        cls = ' class="featured"' if i == 0 else ""
        items.append(f'''<li data-cat="{esc(p["category"])}"{cls}><a class="post-card" href="/blog/{p["slug"]}/"><span class="chip">{esc(p["category"])}</span><h2>{esc(p["title"])}</h2><p>{esc(p["description"])}</p><span class="pc-meta"><time datetime="{iso(p["date"])}">{dot(p["date"])}</time><span>약 {p["minutes"]}분</span></span></a></li>''')
    body = f'''{header()}
<main id="main">
<div class="bl-wrap">
<section class="bl-hero">
<nav class="crumb" aria-label="현재 위치"><a href="/">홈</a><span aria-hidden="true">›</span><span>블로그</span></nav>
<p class="kicker">BLOG / 디스코드 가이드</p>
<h1>디스코드, <span>제대로</span> 쓰는 법</h1>
<p class="lead">{desc}</p>
</section>
<div class="cat-bar" role="group" aria-label="카테고리">{chips}</div>
<ul class="post-grid">
{chr(10).join(items)}
</ul>
</div>
</main>
{FOOTER}'''
    return page(head, body)

# ---------------------------------------------------------------- RSS · 사이트맵 · llms.txt
def render_feed(posts):
    now = format_datetime(datetime.now(KST))
    items = "".join(f'''
  <item>
   <title>{esc(p["title"])}</title>
   <link>{SITE}/blog/{p["slug"]}/</link>
   <guid isPermaLink="true">{SITE}/blog/{p["slug"]}/</guid>
   <category>{esc(p["category"])}</category>
   <pubDate>{format_datetime(datetime.fromisoformat(p["date"]).replace(tzinfo=KST))}</pubDate>
   <description>{esc(p["description"])}</description>
  </item>''' for p in posts)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
 <channel>
  <title>Rito0223 디스코드 가이드 블로그</title>
  <link>{SITE}/blog/</link>
  <atom:link href="{SITE}/blog/feed.xml" rel="self" type="application/rss+xml"/>
  <description>디스코드 서버 세팅·서버부스트·니트로·보안 정보 가이드</description>
  <language>ko</language>
  <lastBuildDate>{now}</lastBuildDate>{items}
 </channel>
</rss>
'''


def render_sitemap(posts):
    imgs = "".join(f'\n    <image:image><image:loc>{SITE}/images/premium/{n}.png</image:loc><image:title>디스코드 서버제작 프리미엄 상세 {n}</image:title></image:image>' for n in range(1, 8))
    latest = max(p["updated"] for p in posts)
    rows = [f'''  <url>
    <loc>{SITE}/</loc><lastmod>{HOME_MODIFIED}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority>
    <image:image><image:loc>{OG_IMAGE}</image:loc><image:title>Rito0223 디스코드 서버제작·니트로·서버부스트</image:title></image:image>{imgs}
  </url>''']
    for path in ("discord-server-creation", "discord-nitro", "discord-server-boost"):
        rows.append(f"  <url><loc>{SITE}/{path}/</loc><lastmod>{SERVICE_MODIFIED}</lastmod><changefreq>monthly</changefreq><priority>0.9</priority></url>")
    rows.append(f"  <url><loc>{SITE}/blog/</loc><lastmod>{latest}</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>")
    for p in posts:
        rows.append(f"  <url><loc>{SITE}/blog/{p['slug']}/</loc><lastmod>{p['updated']}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def render_llms(posts):
    latest = max([p["updated"] for p in posts] + [HOME_MODIFIED])
    blog_lines = "\n".join(f"- [{p['title']}]({SITE}/blog/{p['slug']}/): {p['description']}" for p in posts)
    return f"""# Rito0223 (리토 디스코드)

> Rito0223은 디스코드 서버제작 대행(일반 4,000원부터 · 프리미엄 10,000원), 디스코드 봇 제작/세팅(1,000원부터), 디스코드 니트로·니트로 베이직, 디스코드 서버부스트(레벨 1·2·3)를 판매·대행하는 한국 서비스입니다. 문의와 거래는 카카오톡 채널 또는 번개장터에서 진행하며, 번개장터 기준 누적 판매 450건 이상·후기 300건 이상입니다.

공식 사이트: {SITE}/
최종 업데이트: {latest}
언어: 한국어 (서비스 지역: 대한민국)

## 서비스 페이지

- [홈]({SITE}/): 전체 상품, 상품별 상세(사진·포함 내용), 서버부스트 레벨 가이드, 진행 방식, 자주 묻는 질문
- [디스코드 서버제작 대행]({SITE}/discord-server-creation/): 일반(4,000원~)과 프리미엄(10,000원) 차이, 진행 과정, 비용, FAQ
- [디스코드 니트로 vs 니트로 베이직]({SITE}/discord-nitro/): 두 요금제의 혜택 비교와 구매 방법
- [디스코드 서버부스트 레벨별 차이]({SITE}/discord-server-boost/): 레벨 1·2·3 부스트 요건(2·7·14개)과 혜택, 구매 방법

## 블로그 (디스코드 정보 가이드)

- [블로그 목록]({SITE}/blog/): 디스코드 서버 세팅·채널 꾸미기·서버부스트·니트로·보안 정보 글 모음
{blog_lines}

## 핵심 정보

### 디스코드 서버제작
- 일반 (4,000원부터): 기본 채널·카테고리 구성, 기본 역할·권한 설정, 봇 1종 기본 연동
- 프리미엄 (10,000원): 출고시간 1시간 이내, 출고 후 수정 5회, 제작 후 무제한 수정, 유행하는 이모지 추가, 이모티콘·특수문자로 채널 꾸미기, 모든 봇 세팅, 테러 방지봇, 테러 방지를 위한 모든 행동 로그화, 프리미엄 고객 문의 최우선
- 진행: 문의 → 1:1 상담 → 제작 → 전달·확인(필요 시 수정)

### 디스코드 봇 제작/세팅
- 봇 세팅 대행 1,000원부터, 원하는 기능의 맞춤 봇 제작은 최저가 견적
- 월 유지비 없이 봇을 운영하는 방법 안내, 사후 관리 포함

### 디스코드 니트로
- 니트로 베이직: 모든 서버에서 커스텀 이모지·스티커, 파일 업로드 50MB, 서버 부스트 미포함
- 니트로: 파일 업로드 500MB, HD 스트리밍(최대 4K 60fps), 서버 부스트 2개 + 추가 부스트 30% 할인, 애니메이션 아바타·프로필
- 구매: 원하는 종류와 기간을 카카오톡 또는 번개장터로 알려주면 안내

### 디스코드 서버부스트 (디스코드 공식 기준)
- 레벨 1 (부스트 2개): 이모지 100칸, 스티커 15칸, 오디오 128kbps, 애니메이션 서버 아이콘, 화면공유 720p 60fps
- 레벨 2 (부스트 7개): 이모지 150칸, 스티커 30칸, 오디오 256kbps, 업로드 50MB, 서버 배너, 화면공유 1080p 60fps
- 레벨 3 (부스트 14개): 이모지 250칸, 스티커 60칸, 오디오 384kbps, 업로드 100MB, 커스텀 초대 링크(vanity URL), 애니메이션 서버 배너
- 구매: 목표 레벨을 알려주면 필요한 부스트 수량과 함께 안내

### 로켓지급 · 무상 AS
- 로켓지급: 로켓지급 상품은 구매 후 1시간 내 지급
- 무상 AS: 상품별로 고지된 보증 기간 안에 문제가 생기면 무상 AS

## 문의·거래

- [카카오톡 채널 채팅]({KAKAO}): 1:1 상담, 메시지는 언제든 남기면 순서대로 답변
- [번개장터 상점]({BUNJANG_SHOP}): 상품 확인 및 안전 거래, 판매·후기 집계 기준

## 참고

- 니트로·서버부스트 혜택 수치는 디스코드 정책에 따라 바뀔 수 있습니다. 출처: 디스코드 공식 고객센터 「서버 부스트 FAQ」, 「Nitro & Nitro Basic은 무엇입니까?」
"""


ROBOTS = """# Rito0223 - 디스코드 서버제작 · 니트로 · 서버부스트
# 모든 검색엔진 및 AI 검색엔진 전체 허용

User-agent: *
Allow: /
Disallow: /_blog-src/

# ---- 주요 검색엔진 ----
User-agent: Googlebot
Allow: /

User-agent: Googlebot-Image
Allow: /

User-agent: Bingbot
Allow: /

# 네이버
User-agent: Yeti
Allow: /

# 다음
User-agent: Daum
Allow: /

User-agent: Daumoa
Allow: /

# ---- AI 검색엔진 (AI 답변에 인용되도록 허용) ----
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: DuckAssistBot
Allow: /

User-agent: Meta-ExternalAgent
Allow: /

# AI용 요약 문서
# https://www.rito0223.com/llms.txt

Sitemap: https://www.rito0223.com/sitemap.xml
"""

# ---------------------------------------------------------------- 실행
def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("  만듦:", rel)


def main():
    posts = load_posts()
    slugs = [p["slug"] for p in posts]
    if len(slugs) != len(set(slugs)):
        sys.exit("[오류] slug가 겹치는 글이 있어요")
    print(f"글 {len(posts)}개를 빌드합니다 → {ROOT}")
    for p in posts:
        write(f"blog/{p['slug']}/index.html", render_post(p, posts))
    write("blog/index.html", render_index(posts))
    write("blog/feed.xml", render_feed(posts))
    for name in ("blog.css", "blog.js"):
        shutil.copyfile(os.path.join(HERE, "assets", name), os.path.join(ROOT, "blog", name))
        print("  복사:", f"blog/{name}")
    write("sitemap.xml", render_sitemap(posts))
    write("llms.txt", render_llms(posts))
    write("robots.txt", ROBOTS)
    print("완료!")


if __name__ == "__main__":
    main()
