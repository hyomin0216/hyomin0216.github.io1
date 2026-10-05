# rito0223.com

GitHub Pages(Jekyll)로 배포되는 Rito0223 사이트입니다.

## 폴더 구조

| 경로 | 역할 |
| --- | --- |
| `index.html`, `discord-*/` | 홈·상품 페이지 (직접 작성한 HTML) |
| `_posts/` | **블로그 글** (마크다운 파일 1개 = 글 1개) |
| `_layouts/post.html` | 블로그 글 디자인 템플릿 (SEO 태그·구조화 데이터 자동 생성) |
| `_includes/` | 헤더·푸터·공통 head |
| `_data/services.yml` | 글 하단 "관련 서비스" 박스 문구 |
| `blog/` | 블로그 목록 페이지, 블로그 CSS, RSS(feed.xml 자동 생성) |
| `images/blog/` | 블로그 이미지 |
| `.pages.yml` | Pages CMS 글쓰기 화면 설정 |

`sitemap.xml`, `llms.txt`, 블로그 목록, 홈의 "디스코드 가이드" 섹션은 글을 올리면 자동으로 갱신됩니다.

## 글 쓰는 방법

### A. Pages CMS (추천)
1. https://app.pagescms.org 접속 → GitHub로 로그인
2. 이 저장소 선택 → **블로그 글** → 새 글
3. 제목·주소(영문)·요약 설명·본문 입력 후 저장 → 1~2분 뒤 사이트에 반영

### B. 파일 직접 올리기
`_posts/` 폴더에 `YYYY-MM-DD-영문-주소.md` 파일을 올립니다. 맨 위 머리말 형식은 기존 글을 복사해서 쓰면 됩니다.

```yaml
---
title: 글 제목 (검색 키워드를 앞쪽에)
slug: english-url-slug
description: 검색결과에 보일 요약 문장 (80~150자)
date: 2026-10-05
category: 서버 세팅 가이드
tags: [키워드1, 키워드2]
service: server-creation   # nitro / server-boost
summary:
  - 결론부터 한 줄 요약
faq:
  - q: 질문
    a: 답변
---
본문 (마크다운)
```

- 임시저장: 머리말에 `published: false`
- 내용을 고쳤다면: `updated: 2026-11-01` 추가 (검색엔진에 최신 글로 표시)
