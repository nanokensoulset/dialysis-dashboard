import requests
from bs4 import BeautifulSoup
import pandas as pd

# ニュースを取得
def fetch_news():
    url = "https://www.kidney-international.org/current"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        articles = [a.text.strip() for a in soup.select("h3 a")][:5]
        return articles if articles else ["ニュースを取得できませんでした"]
    except Exception:
        return ["ニュース取得エラー"]

# 論文を取得
def fetch_papers():
    url = "https://pubmed.ncbi.nlm.nih.gov/?term=dialysis"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        titles = [a.text.strip() for a in soup.select(".docsum-title")][:5]
        return titles if titles else ["論文を取得できませんでした"]
    except Exception:
        return ["論文取得エラー"]

# メーカー情報を取得
def fetch_manufacturer_info():
    url = "https://www.nipro.co.jp/products/dialysis/"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        items = [li.text.strip() for li in soup.select("li")][:5]
        return items if items else ["メーカー情報を取得できませんでした"]
    except Exception:
        return ["メーカー情報取得エラー"]
