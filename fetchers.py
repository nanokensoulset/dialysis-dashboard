import requests
import feedparser
from urllib.parse import quote_plus

def fetch_news(queries=None, max_items=20, lang="ja", region="JP"):
    """
    GoogleニュースRSSを requests(+UA) で取得 → feedparser で解析。
    3種類のURL形式に自動リトライし、最初に成功したものを採用。
    失敗時は空リストを返す（アプリ側でメッセージ表示）。
    """
    if queries is None:
        queries = ["透析 技術", "ダイアライザー", "HDF OR hemodiafiltration"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0 Safari/537.36"
    }
    # URL候補（環境によって通る/通らない差がある）
    url_patterns = [
        "https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={gl}:{hl}",
        "https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={gl}%3A{hl}",
        # 旧形式（地域パラメータなし）
        "https://news.google.com/rss/search?q={q}&hl={hl}"
    ]

    rows = []
    for q in queries:
        q_enc = quote_plus(q)
        success_this_query = False
        for pat in url_patterns:
            url = pat.format(q=q_enc, hl=lang, gl=region)
            try:
                r = requests.get(url, headers=headers, timeout=12)
                r.raise_for_status()
                feed = feedparser.parse(r.content)  # 文字列でなく bytes を渡すのが安定
                if getattr(feed, "entries", None):
                    for e in feed.entries[:max_items]:
                        title = getattr(e, "title", "").strip()
                        link = getattr(e, "link", "")
                        source = getattr(getattr(e, "source", None), "title", None) or getattr(e, "author", None) or "Google News"
                        if title and link:
                            rows.append({"title": title, "url": link, "source": source})
                        if len(rows) >= max_items:
                            break
                    success_this_query = len(rows) > 0
            except Exception:
                # 次のURL候補で再試行
                pass

            if success_this_query:
                break  # このクエリはOKだったので次のクエリへ

        if len(rows) >= max_items:
            break  # 全体の上限に達したら終了

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
