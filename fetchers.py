import requests
from bs4 import BeautifulSoup
import pandas as pd
import feedparser
from urllib.parse import quote_plus

# ✅ GoogleニュースRSSを使って安全にニュースを取得
def fetch_news(queries=None, max_items=20, lang="ja", region="JP"):
    """
    GoogleニュースRSSで透析関連ニュースを取得。
    到達できなかった場合はフォールバックURLでも試す。
    戻り値: [{'title':..., 'url':..., 'source':...}, ...]
    """
    if queries is None:
        queries = ["透析 技術", "ダイアライザー", "HDF OR hemodiafiltration"]

    rows = []
    # 正式：q=...&hl=ja&gl=JP&ceid=JP:ja
    base1 = "https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={gl}:{hl}"
    # フォールバック：順序違いでも対応
    base2 = "https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={gl}%3A{hl}"

    for q in queries:
        for base in (base1, base2):
            url = base.format(q=quote_plus(q), hl=lang, gl=region)
            feed = feedparser.parse(url)
            if getattr(feed, "bozo", 0) and not getattr(feed, "entries", None):
                continue  # 次のbaseで再試行
            for e in feed.entries[:max_items]:
                title = getattr(e, "title", "").strip()
                link = getattr(e, "link", "")
                source = getattr(getattr(e, "source", None), "title", None) or getattr(e, "author", None) or "Google News"
                if title and link:
                    rows.append({"title": title, "url": link, "source": source})
                if len(rows) >= max_items:
                    break
            if rows:
                break  # このクエリは取得できたので次のクエリへ
        if len(rows) >= max_items:
            break

    return rows  # 0件ならアプリ側で空表示

# （下の2つはそのままでOK。あとでRSS/API版に切替予定）
def fetch_papers():
    url = "https://pubmed.ncbi.nlm.nih.gov/?term=dialysis"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        titles = [a.text.strip() for a in soup.select(".docsum-title")][:5]
        return titles if titles else ["論文を取得できませんでした"]
    except Exception:
        return ["論文取得エラー"]

def fetch_manufacturer_info():
    url = "https://www.nipro.co.jp/products/dialysis/"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        items = [li.text.strip() for li in soup.select("li")][:5]
        return items if items else ["メーカー情報を取得できませんでした"]
    except Exception:
        return ["メーカー情報取得エラー"]
