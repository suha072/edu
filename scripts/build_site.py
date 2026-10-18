"""materials/ 아래 교재를 _site/로 복사하고, 교재 목록 페이지(_site/index.html)를 만든다.

교재 하나는 materials/<slug>/index.html 파일이다. slug는 사이트 주소에 그대로 쓰이므로
영어 소문자, 숫자, 하이픈만 쓴다. 목록 카드에 보이는 제목과 설명은 각 교재의
<title>과 <meta name="description">에서 읽는다.

사용법: python3 scripts/build_site.py
"""
import html
import re
import shutil
import subprocess
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATERIALS = ROOT / "materials"
OUT = ROOT / "_site"
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class MetaReader(HTMLParser):
    """교재 HTML에서 <title>과 <meta name="description">만 읽는다."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta" and (a.get("name") or "").lower() == "description":
            self.description = (a.get("content") or "").strip()

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def added_date(path):
    """교재 폴더가 git에 처음 커밋된 날짜를 돌려준다.

    아직 커밋하지 않은 교재는 오늘 날짜로 본다. GitHub Actions에서는 checkout을
    fetch-depth: 0으로 받아야 한다. 이력이 한 커밋뿐이면 모든 교재가 그 커밋 날짜가 된다.
    """
    try:
        dates = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%cs", "--", str(path)],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        dates = []
    return dates[-1] if dates else date.today().isoformat()


def read_materials():
    items, errors = [], []
    for d in sorted(p for p in MATERIALS.iterdir() if p.is_dir()):
        rel = d.relative_to(ROOT)
        if not SLUG_RE.match(d.name):
            errors.append(f"{rel}: 폴더 이름은 사이트 주소에 쓰이므로 영어 소문자, 숫자, 하이픈만 쓸 수 있습니다.")
            continue
        page = d / "index.html"
        if not page.is_file():
            errors.append(f"{rel}: index.html 파일이 없습니다.")
            continue
        reader = MetaReader()
        reader.feed(page.read_text(encoding="utf-8"))
        items.append({
            "slug": d.name,
            "title": reader.title.strip() or d.name,
            "description": reader.description,
            "added": added_date(d),
        })
    if errors:
        sys.exit("\n".join(errors))
    # 최근에 올린 교재가 목록 위쪽에 오도록 정렬한다.
    items.sort(key=lambda it: it["added"], reverse=True)
    return items


def render_index(items):
    cards = []
    for it in items:
        desc = f'<span class="d">{html.escape(it["description"])}</span>' if it["description"] else ""
        cards.append(
            f'<li><a href="{it["slug"]}/"><span class="t">{html.escape(it["title"])}</span>'
            f'{desc}<span class="date">{it["added"]}에 올림</span></a></li>'
        )
    if not cards:
        cards.append('<li class="empty">아직 올린 교재가 없습니다.</li>')
    return INDEX_TEMPLATE.replace("{{ITEMS}}", "\n".join(cards))


INDEX_TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>교재 모음</title>
<style>
/* 색상은 교재 페이지와 같은 값을 쓰고, 기기가 다크 모드이면 어두운 값으로 바꾼다. */
:root{--bg:#faf9f5;--card:#ffffff;--text:#1f1e1d;--muted:#73726c;--line:rgba(0,0,0,.12);--accent:#185FA5}
@media (prefers-color-scheme: dark){
  :root{--bg:#1f1e1d;--card:#2a2927;--text:#f1efe8;--muted:#b4b2a9;--line:rgba(255,255,255,.14);--accent:#85B7EB}
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR","Malgun Gothic",sans-serif;
  line-height:1.5}
main{max-width:920px;margin:0 auto;padding:24px 16px calc(24px + env(safe-area-inset-bottom))}
h1{font-size:22px;font-weight:600;margin:0}
.sub{color:var(--muted);font-size:14px;margin:4px 0 20px}
/* 카드는 휴대폰에서 한 줄에 하나, 태블릿에서 두세 개씩 놓인다. */
ul{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(min(260px,100%),1fr));
  list-style:none;margin:0;padding:0}
li a{display:flex;flex-direction:column;gap:6px;height:100%;min-height:96px;padding:16px;
  border:1px solid var(--line);border-radius:16px;background:var(--card);color:inherit;text-decoration:none;
  touch-action:manipulation;-webkit-tap-highlight-color:transparent}
li a:active{transform:scale(.98)}
li a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.t{font-size:18px;font-weight:600;color:var(--accent)}
.d{font-size:14px;color:var(--muted)}
.date{margin-top:auto;font-size:12px;color:var(--muted)}
.empty{color:var(--muted)}
</style>
</head>
<body>
<main>
<h1>교재 모음</h1>
<p class="sub">휴대폰과 태블릿에서 터치로 쓰는 교재입니다. 카드를 누르면 교재가 열립니다.</p>
<ul>
{{ITEMS}}
</ul>
</main>
</body>
</html>
"""


def main():
    items = read_materials()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for it in items:
        shutil.copytree(MATERIALS / it["slug"], OUT / it["slug"])
    (OUT / "index.html").write_text(render_index(items), encoding="utf-8")
    print(f"교재 {len(items)}개로 {OUT.relative_to(ROOT)}/ 를 만들었습니다.")


if __name__ == "__main__":
    main()
