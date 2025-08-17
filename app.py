import streamlit as st
import pandas as pd
from datetime import date, timedelta
from fetchers import fetch_google_news, fetch_pubmed, fetch_manufacturer_news, load_conferences

st.set_page_config(page_title="透析技術ダッシュボード", layout="centered")

st.markdown("""
<style>
.stButton > button { padding: 0.8rem 1.1rem; font-size: 1.05rem; }
a { word-break: break-word; }
.card { border: 1px solid #e6e6e6; border-radius: 12px; padding: 12px; margin-bottom: 10px; background: #fff; }
.card h4 { margin: 0 0 6px 0; font-size: 1.05rem;}
.card small { color: #666; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 12px; background: #efefef; margin-right: 6px; font-size: 0.8rem;}
.section-title { margin-top: 0.6rem; }
</style>
""", unsafe_allow_html=True)

st.title("📱 透析技術ダッシュボード")
st.caption("ニュース ＞ 論文 ＝ トレンド ＝ メーカー情報 + 学会情報（日本）")

with st.sidebar:
    st.subheader("更新・絞り込み")
    days = st.select_slider("新着の期間", options=[3,7,14,30,90], value=14)
    q_user = st.text_input("キーワード（空欄で透析ニュース）", value="人工透析 OR 透析 技術 OR ダイアライザー OR HDF")
    st.caption("例: 'ダイアライザー 膜', 'online HDF', 'dialyzer technology'")
    run = st.button("🔄 データ更新")
    st.markdown("---")
    st.caption("※ 取得は合法なRSS/APIのみを使用しています。")

if "news_df" not in st.session_state or run:
    news_queries = [q_user, "dialyzer technology OR hemodialysis device", "HDF OR hemodiafiltration 技術"]
    st.session_state.news_df = fetch_google_news(news_queries, max_items=50)

if "paper_df" not in st.session_state or run:
    term = '(hemodialysis OR dialysis OR "hemodiafiltration" OR HDF) AND (technology OR device OR dialyzer)'
    st.session_state.paper_df = fetch_pubmed(term, retmax=30, email="example@example.com")

if "maker_df" not in st.session_state or run:
    st.session_state.maker_df = fetch_manufacturer_news(max_items=40)

if "conf_df" not in st.session_state or run:
    st.session_state.conf_df = load_conferences("data/conferences.csv")

news_df = st.session_state.news_df
paper_df = st.session_state.paper_df
maker_df = st.session_state.maker_df
conf_df = st.session_state.conf_df

since = date.today() - timedelta(days=days)
news_df_f = news_df[news_df["date"].fillna(pd.Timestamp.today().date()) >= since]
paper_df_f = paper_df[paper_df["date"].fillna(pd.Timestamp.today().date()) >= since]
maker_df_f = maker_df[maker_df["date"].fillna(pd.Timestamp.today().date()) >= since]

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📰 ニュース","📚 論文","🏭 メーカー情報","📊 トレンド","🗓 学会情報"])

def render_cards(df: pd.DataFrame, empty_text="該当データがありません。"):
    if df.empty:
        st.info(empty_text); return
    for _, r in df.sort_values("date", ascending=False).iterrows():
        dt = r["date"].strftime("%Y-%m-%d") if pd.notna(r["date"]) else ""
        source = r.get("source","")
        url = r.get("url","")
        tags = r.get("tags", []) or []
        summary = r.get("summary","")
        badges = ''.join([f'<span class="badge">{t}</span>' for t in tags]) if tags else ''
        st.markdown(f"""
        <div class="card">
          <h4><a href="{url}" target="_blank">{r["title"]}</a></h4>
          <small>{dt}　{source}</small><br/>
          <div style="margin:6px 0;">{summary}</div>
          <div>{badges}</div>
        </div>
        """, unsafe_allow_html=True)

with tab1:
    st.header("📰 透析ニュース")
    render_cards(news_df_f, "新しいニュースが見つかりませんでした。")

with tab2:
    st.header("📚 新着論文（PubMed）")
    render_cards(paper_df_f, "新しい論文が見つかりませんでした。")

with tab3:
    st.header("🏭 メーカー情報")
    render_cards(maker_df_f, "メーカーの新着が見つかりませんでした。")

with tab4:
    st.header("📊 トレンド（タグ件数・最近）")
    all_df = pd.concat([news_df_f, paper_df_f, maker_df_f], ignore_index=True)
    if all_df.empty:
        st.info("最近のデータが少ないため、トレンドを表示できません。")
    else:
        exploded = all_df.explode("tags")
        trend = exploded.groupby("tags")["title"].count().sort_values(ascending=False).reset_index()
        st.dataframe(trend, use_container_width=True)

with tab5:
    st.header("🗓 日本の透析関連 学会情報")
    render_cards(conf_df, "学会情報が未登録です。data/conferences.csv を追加してください。")

st.caption("© Dialysis Tech Dashboard — legal sources only (Google News RSS, PubMed API, public conference pages).")
