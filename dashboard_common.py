from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
px.defaults.color_discrete_sequence = ["#1DB954", "#b3b3b3", "#0f5c2e", "#f0f0f0", "#168a3d", "#747b75", "#29cf66", "#c7d3c9", "#124d29", "#8f9b91", "#65d98a", "#e5e5e5"]
px.defaults.color_continuous_scale = [[0, "#0f5c2e"], [0.5, "#1DB954"], [1, "#d9f2df"]]


def configure_page(title: str, icon: str = "🎵") -> None:
    st.set_page_config(page_title=f"{title} | Spotify Music Dashboard", page_icon=icon, layout="wide")
    st.markdown("""
    <style>
    .stApp { background:#121212; color:#fff; }
    h1,h2,h3,h4,p,li,label,span,small { color:#fff; }
    .stMarkdown, .stCaption, [data-testid="stWidgetLabel"] { color:#fff !important; }
    div[data-testid="stMetric"] { background:#242424; border-left:4px solid #1DB954; padding:16px; border-radius:12px; }
    div[data-testid="stMetricLabel"] { color:#b3b3b3 !important; }
    div[data-testid="stMetricValue"] { color:#1DB954 !important; }
    section[data-testid="stSidebar"] { background:#000; }
    header[data-testid="stHeader"] { background:transparent; }
    section[data-testid="stSidebar"] div[data-testid="stSidebarContent"] { display:flex !important; flex-direction:column !important; justify-content:flex-start !important; }
    section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] { order:1; flex:0 0 auto; padding-top:0 !important; padding-bottom:0 !important; }
    section[data-testid="stSidebar"] div[data-testid="stSidebarNav"] { order:2; flex:0 0 auto; margin:0 !important; padding-top:.8rem !important; padding-bottom:1rem; }
    a[data-testid="stSidebarNavLink"] { color:#fff !important; font-weight:400 !important; }
    a[data-testid="stSidebarNavLink"] span { color:#fff !important; font-weight:400 !important; }
    div[data-testid="stSidebarNav"] a[data-testid="stSidebarNavLink"]:hover { color:#1ed760 !important; background:#1b1b1b !important; }
    input,textarea,[data-baseweb="select"] { color:#fff !important; }
    div[data-testid="stDataFrame"] { color:#fff; }
    div[data-baseweb="select"] [data-baseweb="tag"] { background:#0f5c2e !important; border:1px solid #1DB954 !important; }
    div[data-baseweb="select"] [data-baseweb="tag"] * { color:#1ed760 !important; font-weight:600 !important; }
    div[role="listbox"] [role="option"][aria-selected="true"] { background:#0f5c2e !important; color:#1ed760 !important; }
    div[role="listbox"] [role="option"][aria-selected="true"] * { color:#1ed760 !important; }
    .sidebar-brand-title { color:#1DB954; font-size:34px; line-height:34px; font-weight:750; margin:0; }
    .sidebar-brand-copy { color:#fff; font-size:1rem; line-height:1.25; font-weight:700; margin:0; white-space:nowrap; }
    .sidebar-brand-project { color:#fff; font-size:.92rem; line-height:1.25; font-weight:400; }
    div[data-testid="stSidebarUserContent"] .stMarkdown { margin-top:0 !important; margin-bottom:0 !important; }
    [class*="st-key-compact"] [data-testid="stMetricValue"] { font-size:1.35rem !important; }
    [class*="st-key-compact"] [data-testid="stMetricLabel"] { font-size:.78rem !important; }
    [class*="st-key-user_recs_table"] [data-testid="stDataFrame"] { border:1px solid #0f5c2e; border-radius:8px; }
    .st-key-rec_user_select [data-baseweb="select"] > div { background:#242424 !important; border-color:#0f5c2e !important; }
    .st-key-rec_user_select [data-baseweb="select"] * { color:#1DB954 !important; }
    </style>
    """, unsafe_allow_html=True)
    active_path = {
        "Executive Summary": "executive-summary",
        "Audience & Catalog Insights": "audience-catalog-insights",
        "Recommendation Analytics": "recommendation-analytics",
        "Graph Analytics & Discovery": "graph-analytics-discovery",
    }.get(title)
    if active_path:
        st.markdown(f"""
        <style>
        a[data-testid="stSidebarNavLink"][href*="{active_path}"] {{ color:#000 !important; background:#1DB954 !important; font-weight:700 !important; border-radius:8px !important; }}
        a[data-testid="stSidebarNavLink"][href*="{active_path}"] span {{ color:#000 !important; font-weight:700 !important; }}
        </style>
        """, unsafe_allow_html=True)
    icon_col, title_col = st.sidebar.columns([0.12, 0.88], vertical_alignment="center", gap="small")
    icon_col.image(str(ROOT / "Spotify_icon.png"), width=34)
    title_col.markdown('<div class="sidebar-brand-title">Spotify</div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        '<div class="sidebar-brand-copy">Music Recommendation Dashboard<br><span class="sidebar-brand-project">Big Data Analytics Final Project</span></div>',
        unsafe_allow_html=True,
    )


@st.cache_data
def load_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Required data file not found: {path}")
    return pd.read_csv(path)


def load_optional(filename: str) -> pd.DataFrame:
    try:
        return load_csv(filename)
    except FileNotFoundError:
        return pd.DataFrame()


def finish_page() -> None:
    st.markdown("---")
    st.caption("Spotify Music Recommendation Dashboard | Big Data Analytics")


def style_chart(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#121212",
        plot_bgcolor="#121212",
        font_color="white",
        colorway=["#1DB954", "#b3b3b3", "#0f5c2e", "#f0f0f0", "#168a3d", "#747b75", "#29cf66", "#c7d3c9", "#124d29", "#8f9b91", "#65d98a", "#e5e5e5"],
        legend=dict(font=dict(color="#e5e5e5")),
    )
    for trace in fig.data:
        if trace.type == "pie":
            trace.marker.line.width = 1
            trace.marker.line.color = "#121212"
    return fig


def spotify_table(data: pd.DataFrame):
    return data.style.set_table_attributes('style="width:100%"').set_properties(
        **{"background-color": "#242424", "color": "#1DB954", "border-color": "#0f5c2e"}
    ).set_table_styles(
        [
            {"selector": "th", "props": [("background-color", "#242424"), ("color", "#1DB954"), ("border-color", "#0f5c2e")]},
            {"selector": "td", "props": [("border-color", "#0f5c2e")]},
        ]
    )
