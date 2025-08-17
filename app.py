import streamlit as st
import pandas as pd
from datetime import date, timedelta
from fetchers import fetch_news, fetch_papers, fetch_manufacturer_info

st.set_page_config(page_title="透析技術ダッシュボード", layout="centered")

st.markdown("""
<style>
/* 文字色とフォントを固定して、ダークでも消えないようにする */
html, body, [class^="st-"], .stMarkdown, .stText, .stCaption {
  color: #111 !important;
  font-family: -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans JP","Hiragino Kaku Gothic ProN","Meiryo",sans-serif !important;
}

/* カードの見やすさ */
.card {
  border: 1px solid #e6e6e6; border-radius: 12px; padding: 12px; margin-bottom: 10px; background: #fff;
}
.card h4 { margin: 0 0 6px 0; font-size: 1.05rem; }
.card small { color: #444; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 12px; background: #efefef; margin-right: 6px; font-size: 0.8rem; }

/* 端末がダーク設定でも読めるように上書き */
@media (prefers-color-scheme: dark) {
  html, body, [class^="st-"], .stMarkdown, .stText, .stCaption { color: #f5f5f5 !important; }
  .card { background: #1f1f1f; border-color: #333; }
  .card small { color: #bbb; }
  .badge { background: #333; }
}
</style>
""", unsafe_allow_html=True)


st.title("📱 透析技術ダッシュボード（簡易版）")
st.caption("ニュース ＞ 論文 ＝ メーカー情報 ＋ 学会情報")

# サイドバー
with st.sidebar:
    st.subheader("更新")
    if st.button("🔄 最新取得"):
        st.session_state.pop("news", None)
        st.session_state.pop("papers", None)
        st.session_state.pop("makers", None)

# 取得（シンプル実装）
if "news" not in st.session_state:
    st.session_state.news = fetch_news()
if "papers" not in st.session_state:
    st.session_state.papers = fetch_papers()
if "makers" not in st.session_state:
    st.session_state.makers = fetch_manufacturer_info()

news = st.session_state.news
papers = st.session_state.papers
makers = st.session_state.makers

tab1, tab2, tab3, tab4 = st.tabs(["📰 ニュース","📚 論文","🏭 メーカー情報","🗓 学会情報"])

def render_list(items, empty_msg):
    if not items:
        st.info(empty_msg)
        return
    for t in items:
        # dict（タイトル＋URL）の場合はリンクで表示、文字列ならそのまま
        if isinstance(t, dict):
            title = t.get("title", "")
            url = t.get("url", "")
            source = t.get("source", "")
            st.markdown(
                f'<div class="card"><h4><a href="{url}" target="_blank">{title}</a></h4>'
                f'<small>{source}</small></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(f'<div class="card"><h4>{t}</h4></div>', unsafe_allow_html=True)
    st.header("📰 透析ニュース（簡易）")
    render_list(news, "ニュースが見つかりませんでした。")

with tab2:
    st.header("📚 新着論文（簡易）")
    render_list(papers, "論文が見つかりませんでした。")

with tab3:
    st.header("🏭 メーカー情報（簡易）")
    render_list(makers, "メーカー情報が見つかりませんでした。")

with tab4:
    st.header("🗓 日本の透析関連 学会情報（CSV）")
    try:
        df = pd.read_csv("data/conferences.csv")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.info("学会情報CSVが未作成です。data/conferences.csv を作成してください。")
        st.caption(f"Error: {e}")
