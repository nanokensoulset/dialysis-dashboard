import requests
from bs4 import BeautifulSoup
import pandas as pd
import feedparser
from urllib.parse import quote_plus

# ✅ GoogleニュースRSSを使って安全にニュースを取得
def fetch_news(queries=None, max_items=20, lang="ja", region="JP"):
    if queries is None:
        queries = ["透析 技術", "ダイアライザー", "HDF OR hemodiafiltration"]

    rows = []
    base = "https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={ceid}"
    for q in queries:
        url = base.format(q=quote_plus(q), hl=lang, gl=region, ceid=f"{region}:{lang}")
        feed = feedparser.parse(url)
        for e in feed.entries[:max_items]:
            title = e.title
            link = e.link
            source = getattr(getattr(e, "source", None), "title", None) or getattr(e, "author", None) or "Google News"
            rows.append({"title": title, "url": link, "source": source})
            if len(rows) >= max_items:
                break
    # 文字列リストではなく「辞書のリスト」を返す
    return rows

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
