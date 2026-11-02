"""Rito0223 사이트 공통 정보 (메인·블로그 빌드에서 함께 사용)"""
import json

SITE = "https://www.rito0223.com"
KAKAO = "https://pf.kakao.com/_mSqYxj/chat"
BUNJANG_SHOP = "https://m.bunjang.co.kr/shops/78481327/products"
OG_IMAGE = SITE + "/og-image.png"

ORG = {
    "@type": "Organization",
    "@id": SITE + "/#org",
    "name": "Rito0223",
    "alternateName": ["리토", "리토 디스코드", "Rito"],
    "url": SITE + "/",
    "logo": {"@type": "ImageObject", "url": SITE + "/logo-square.png", "width": 1080, "height": 1080},
    "image": OG_IMAGE,
    "description": "디스코드 서버제작(4,000원~), 디스코드 니트로·니트로 베이직, 디스코드 서버부스트(레벨 1·2·3)를 판매·대행하는 한국 서비스. 번개장터 기준 누적 판매 450건·후기 300건 이상.",
    "areaServed": {"@type": "Country", "name": "대한민국"},
    "knowsAbout": ["디스코드 서버제작", "디스코드 서버 세팅", "디스코드 니트로", "디스코드 니트로 베이직", "디스코드 서버부스트", "디스코드 봇 세팅", "Discord"],
    "contactPoint": {"@type": "ContactPoint", "contactType": "customer service", "url": KAKAO, "availableLanguage": ["ko"]},
    "sameAs": ["https://pf.kakao.com/_mSqYxj", BUNJANG_SHOP],
}

# 메인 페이지에 노출되는 FAQ (화면 표시와 구조화 데이터가 같은 내용을 쓰도록 한 곳에서 관리)
HOME_FAQ = [
    ("디스코드 서버제작 비용은 얼마인가요?", "디스코드 서버제작은 4,000원부터 10,000원 사이이며, 서버 규모와 요청 사항에 따라 상담 후 견적을 안내해 드립니다."),
    ("디스코드 서버제작은 어떻게 진행되나요?", "카카오톡 또는 번개장터로 원하시는 컨셉과 규모를 알려주시면, 채널·카테고리·권한·봇·디자인까지 1:1 상담 후 맞춰 제작합니다."),
    ("디스코드 서버부스트 레벨은 어떻게 다른가요?", "서버부스트는 레벨 1(부스트 2개), 레벨 2(부스트 7개), 레벨 3(부스트 14개)로 나뉩니다. 원하는 레벨을 선택해 문의하시면 안내해 드립니다."),
    ("디스코드 니트로는 어떻게 구매하나요?", "원하시는 종류(니트로 / 니트로 베이직)와 기간을 알려주시면 카카오톡 또는 번개장터로 안내해 드립니다."),
    ("로켓지급과 무상 AS는 무엇인가요?", "로켓지급 상품은 구매 후 1시간 내에 지급해 드려요. 무상 AS는 상품별로 고지된 보증 기간 안에 문제가 생기면 무상으로 AS해 드리는 서비스예요."),
    ("결제와 문의는 어디서 하나요?", "카카오톡 채널 또는 번개장터에서 문의하고 거래할 수 있습니다. 번개장터를 통해 안전하게 거래됩니다."),
    ("Rito0223은 믿을 수 있나요?", "번개장터 기준 누적 판매 450건 이상, 후기 300건 이상을 확인해 제공하고 있어 안심하고 이용하실 수 있습니다."),
    ("상담 가능한 시간이 정해져 있나요?", "메시지는 언제든 남겨주세요. 확인하는 대로 순서대로 답변드립니다."),
]


def faq_schema(page_id, items):
    return {
        "@type": "FAQPage",
        "@id": page_id + "#faq",
        "inLanguage": "ko-KR",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items
        ],
    }


def ld_json(graph):
    data = {"@context": "https://schema.org", "@graph": graph}
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=1) + "\n</script>"


ICONS = """<link rel="icon" href="https://www.rito0223.com/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="48x48" href="https://www.rito0223.com/favicon-48.png">
<link rel="icon" type="image/png" sizes="96x96" href="https://www.rito0223.com/favicon-96.png">
<link rel="icon" type="image/png" sizes="192x192" href="https://www.rito0223.com/favicon.png">
<link rel="apple-touch-icon" sizes="180x180" href="https://www.rito0223.com/apple-touch-icon.png">
<link rel="manifest" href="https://www.rito0223.com/site.webmanifest">"""


def head_meta(title, desc, url, og_type="website", extra=""):
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<meta name="author" content="Rito0223">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="ko" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta name="theme-color" content="#0B0C14">
<meta name="color-scheme" content="dark">
{ICONS}
<meta name="application-name" content="Rito0223">
<meta name="apple-mobile-web-app-title" content="Rito0223">
<link rel="alternate" type="application/rss+xml" title="Rito0223 블로그" href="{SITE}/blog/feed.xml">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Rito0223">
<meta property="og:locale" content="ko_KR">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Rito0223 디스코드 서버제작·니트로·서버부스트">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{OG_IMAGE}">
{extra}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&amp;family=JetBrains+Mono:wght@500;700&amp;display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&amp;family=JetBrains+Mono:wght@500;700&amp;display=swap"></noscript>"""
