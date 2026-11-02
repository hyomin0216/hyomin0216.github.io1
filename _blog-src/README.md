# Rito0223 블로그 관리 방법 (JSON 글 방식)

**글 하나 = JSON 파일 하나**예요. `_blog-src/posts/` 폴더에 JSON 파일을 넣고 GitHub에 올리면,
자동으로 HTML 글 페이지·글 목록·사이트맵·RSS·llms.txt가 만들어져서 사이트에 반영돼요.

> 왜 JSON을 바로 화면에 띄우지 않고 HTML로 바꾸나요?
> 구글·네이버 검색과 ChatGPT·Perplexity 같은 AI 검색은 미리 만들어진 HTML 글을 가장 잘 읽어요.
> 그래서 JSON은 "원고", 자동으로 만들어지는 HTML은 "발행본"이라고 생각하면 돼요.

## 처음 한 번만 할 일

1. 이 폴더 전체를 GitHub 저장소 루트에 올려요. (`.github` 폴더도 꼭 함께)
2. 저장소 **Settings → Pages → Build and deployment → Source** 를 **GitHub Actions** 로 바꿔요.
   - 커스텀 도메인(www.rito0223.com) 설정은 그대로 유지돼요.
3. 이후부터는 올릴 때마다 **Actions** 탭에서 "사이트 빌드 및 배포"가 자동으로 돌아가요. (1~2분)

## 새 글 올리는 법

1. `_blog-src/posts/_template.json` 을 복사해서 이름을 바꿔요. 예: `discord-bot-recommend.json`
   - 파일 이름은 자유지만, 보통 `slug` 와 같게 맞추면 찾기 편해요.
2. 내용을 채우고 `"draft": false` 로 바꿔요. (`true` 면 공개하지 않아요)
3. GitHub에 올리면 끝! (웹에서 **Add file → Upload files** 로 올려도 돼요)

## JSON 항목 설명

| 항목 | 설명 |
|---|---|
| `slug` | 글 주소. 영문 소문자·숫자·하이픈만 → `rito0223.com/blog/slug/` |
| `title` | 제목. 검색 키워드를 앞쪽에 |
| `description` | 검색 결과에 보이는 요약 1~2문장 |
| `category` | 카테고리. 같은 이름끼리 목록에서 묶여요 |
| `date` / `updated` | 작성일 / 수정일 (`2026-11-01` 형식) |
| `keywords` | 키워드 (쉼표로 구분) |
| `draft` | `true` 면 공개 안 함 |
| `cta` | 글 아래 문의 카드: `server`, `premium`, `boost`, `nitro` |
| `tldr` | "핵심 요약" 3~4줄. AI 검색이 가장 많이 인용하는 부분 |
| `content` | 본문 블록 목록 (아래 참고) |
| `faq` | `{ "q": 질문, "a": 답변 }` 목록. 화면 FAQ + 구조화 데이터로 같이 들어가요 |
| `sources` | (선택) 참고 자료 `{ "name": 이름, "url": 주소 }` |

## 본문(content) 블록 종류

```json
{ "h2": "소제목 (목차에 자동으로 들어가요)" }
{ "h3": "작은 소제목" }
{ "p": "문단" }
"따옴표 안에 글만 쓰면 그것도 문단이에요"
{ "ul": ["순서 없는 목록", "항목 2"] }
{ "ol": ["순서 있는 목록", "단계 2"] }
{ "quote": "팁이나 주의사항 박스" }
{ "table": { "head": ["제목1", "제목2"], "rows": [["값", "값"], ["값", "값"]] } }
{ "img": { "src": "/images/blog/사진.png", "alt": "사진 설명", "caption": "아래 설명(선택)" } }
{ "html": "<p>직접 HTML을 넣고 싶을 때</p>" }
```

글 안에서 쓸 수 있는 표기: `**굵게**`, `[링크 글자](/discord-server-boost/)`, `` `코드` ``

## JSON 쓸 때 자주 하는 실수

- 항목 사이 **쉼표(,)** 빠짐 / 마지막 항목 뒤에 쉼표 붙임
- 글 안에 큰따옴표(")를 쓰려면 `\"` 로 쓰거나 “ ” 같은 다른 따옴표 사용
- 틀리면 Actions 탭에 빨간 X와 함께 "몇 번째 줄 근처가 틀렸는지" 한국어로 나와요. 고쳐서 다시 올리면 돼요.

## 내 컴퓨터에서 미리 보기 (선택)

```
python3 _blog-src/build.py
python3 -m http.server 8000
```
브라우저에서 `http://localhost:8000/blog/` 를 열면 돼요.

## SEO / AEO 글쓰기 체크리스트

- 소제목을 사람들이 실제로 검색하는 **질문형**으로 (예: "몇 개부터 효과가 있나요?")
- 소제목 바로 다음 첫 문장에 **답을 먼저**
- 숫자·단계는 표(`table`)나 번호 목록(`ol`)으로
- 본문에서 관련 글과 서비스 페이지로 링크 걸기
- 디스코드 정책 수치는 `sources`에 출처를 남기고, 바뀌면 `updated` 날짜 갱신
