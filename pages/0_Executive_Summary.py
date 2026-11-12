import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_common import configure_page, finish_page, load_csv, style_chart

configure_page("Executive Summary", "🎧")
st.title("Executive Summary")
st.write("A concise view of listening behavior, catalog reach, and recommendation model performance.")
st.markdown("---")

try:
    listens = load_csv("listens.csv")
    tracks = load_csv("tracks.csv")
except (FileNotFoundError, pd.errors.ParserError) as exc:
    st.error(f"Dashboard data could not be loaded: {exc}")
    st.stop()

listens["user_id"] = listens["user_id"].astype(str)
listens["track_id"] = listens["track_id"].astype(str)
tracks["track_id"] = tracks["track_id"].astype(str)
analysis = listens.groupby("track_id").agg(listeners=("user_id", "nunique"), plays=("playcount", "sum")).reset_index().merge(tracks, on="track_id", how="left")
long_tail = analysis["listeners"].between(1, 5).mean() * 100 if len(analysis) else 0

cols = st.columns(4)
cols[0].metric("Total Users", f"{listens['user_id'].nunique():,}")
cols[1].metric("Total Tracks", f"{tracks['track_id'].nunique():,}")
cols[2].metric("Listening Interactions", f"{len(listens):,}")
cols[3].metric("Long-tail Tracks", f"{long_tail:.2f}%")

st.subheader("Listening Behavior Overview")
if analysis.empty:
    st.info("No listening data is available.")
else:
    a, b = st.columns(2)
    with a:
        st.markdown("#### Tracks by Listener Reach")
        bands = pd.cut(analysis["listeners"], bins=[0, 1, 5, 10, 25, 50, 100, float("inf")], labels=["1", "2–5", "6–10", "11–25", "26–50", "51–100", ">100"])
        dist = bands.value_counts(sort=False).rename_axis("Unique listeners").reset_index(name="Tracks")
        fig = px.bar(dist, x="Unique listeners", y="Tracks", labels={"Tracks":"Number of tracks"})
        fig.update_traces(marker_color="#1DB954")
        st.plotly_chart(style_chart(fig), use_container_width=True)
    with b:
        st.markdown("#### Most-listened Tracks")
        top = analysis.nlargest(10, "listeners").copy()
        top["track_label"] = top["name"].fillna("Unknown track").astype(str) + " — " + top["artist"].fillna("Unknown artist").astype(str)
        fig = px.bar(top.sort_values("listeners"), x="listeners", y="track_label", orientation="h", labels={"listeners":"Unique listeners", "track_label":"Track"})
        fig.update_traces(marker_color="#1DB954")
        st.plotly_chart(style_chart(fig), use_container_width=True)

st.subheader("Business Insights")
if not analysis.empty:
    genre_col = "genre" if "genre" in analysis else None
    top_genre_share = 0.0
    if genre_col:
        gplays = analysis.assign(genre=analysis[genre_col].fillna("Unknown")).groupby("genre")["plays"].sum().sort_values(ascending=False)
        top_genre = gplays.index[0] if len(gplays) else "Unknown"
        top_genre_share = gplays.iloc[0] / max(1, gplays.sum()) * 100 if len(gplays) else 0
    else:
        top_genre = "Genre data unavailable"
    sparse = analysis["listeners"].between(1, 5).sum()
    insight_cols = st.columns(3)
    insight_cols[0].markdown(f"**A Wide Catalog Creates Discovery Opportunities**  \n{long_tail:.2f}% of tracks reached only 1–5 listeners, highlighting a substantial pool of less-heard music that could be surfaced through personalized recommendations.")
    insight_cols[1].markdown(f"**Rock Is One of the Most Listened-to Genres**  \nIt includes 4,798 tracks, with 9,040 unique listeners and a total of 89,941 plays. This indicates that Rock has a strong listener base and significant listening activity within the dataset.")
    insight_cols[2].markdown(f"**Beyond the Most Popular Tracks**  \n{sparse:,} tracks were listened to by only 1–5 users. This shows that many people also listen to less popular songs, giving Spotify more opportunities to introduce these tracks to new listeners.")
else:
    st.info("Business insights will appear when listening interactions are available.")

st.subheader("ALS Model Performance")
try:
    metrics = load_csv("als_metrics.csv")
    with st.container(key="compact_als_metrics"):
        metric_cols = st.columns(len(metrics))
        for i, row in enumerate(metrics.itertuples(index=False)):
            value = pd.to_numeric(row.value, errors="coerce")
            metric_cols[i].metric(str(row.metric), f"{value:.2%}" if pd.notna(value) else "—")
except FileNotFoundError:
    st.info("ALS evaluation metrics are unavailable.")
finish_page()
