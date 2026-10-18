#!/usr/bin/env python3
"""扫描 post/*.html，生成根目录 articles.json"""
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
POST_DIR = ROOT / "post"
OUT = ROOT / "articles.json"


def text_of(el):
    return el.get_text(strip=True) if el else ""


def extract(path: Path):
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    # title: h1.article-title > <title>（去掉站点后缀）
    h1 = soup.select_one("h1.article-title")
    if h1:
        title = text_of(h1)
    else:
        t = soup.find("title")
        title = re.sub(r"\s*-\s*zhr的博客\s*$", "", text_of(t)) if t else path.stem

    # excerpt: p.article-excerpt > meta[name=description]
    ex = soup.select_one("p.article-excerpt")
    if ex:
        excerpt = text_of(ex)
    else:
        m = soup.find("meta", attrs={"name": "description"})
        excerpt = (m.get("content") or "").strip() if m else ""

    # date: <time datetime="...">
    time_el = soup.find("time")
    date = (time_el.get("datetime") or "").strip() if time_el else ""

    # image: figure.article-image img > og:image > 第一张 img
    image = ""
    fig = soup.select_one("figure.article-image img")
    if fig and fig.get("src"):
        image = fig["src"].strip()
    if not image:
        og = soup.find("meta", attrs={"property": "og:image"})
        if og and og.get("content"):
            image = og["content"].strip()
    if not image:
        first = soup.find("img")
        if first and first.get("src"):
            image = first["src"].strip()

    # tags: a.article-tag（没有就空数组）
    tags = [text_of(a) for a in soup.select("a.article-tag") if text_of(a)]

    rel = path.relative_to(ROOT).as_posix()
    return {
        "id": rel,
        "title": title,
        "excerpt": excerpt,
        "date": date,
        "link": rel,
        "image": image,
        "tags": tags,
    }


def main():
    files = sorted(POST_DIR.glob("*.html"))
    articles = [extract(f) for f in files]
    # 日期倒序；无日期的排最后，再按路径排序保证稳定
    articles.sort(key=lambda a: (a["date"] or "0000-00-00", a["link"]), reverse=True)
    OUT.write_text(json.dumps(articles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已生成 {OUT}，共 {len(articles)} 篇文章")


if __name__ == "__main__":
    main()