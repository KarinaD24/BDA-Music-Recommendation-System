import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_common import configure_page, finish_page, load_csv, style_chart

configure_page("Audience & Catalog Insights", "👥")
st.title("Audience & Catalog Insights")
st.write("Understand listening reach and how the catalog is distributed across artists, genres, and tracks.")
try:
    users, listens = load_csv("users.csv"), load_csv("listens.csv")
    tracks = load_csv("track_analytics.csv")
    artists, genres = load_csv("artist_analytics.csv"), load_csv("genre_analytics.csv")
except FileNotFoundError as exc:
    st.error(str(exc)); st.stop()

for col in ("genre", "year"):
    if col not in tracks: tracks[col] = "Unknown" if col == "genre" else pd.NA
tracks["year"] = pd.to_numeric(tracks["year"], errors="coerce")
f1, f2 = st.columns(2)
genre_options = sorted(tracks["genre"].dropna().astype(str).unique())
selected_genres = f1.multiselect("Genre", genre_options, placeholder="All genres")
year_options = sorted(tracks["year"].dropna().astype(int).unique())
selected_years = f2.multiselect("Release Year", year_options, placeholder="All years")
view = tracks.copy()
if selected_genres: view = view[view["genre"].astype(str).isin(selected_genres)]
if selected_years: view = view[view["year"].isin(selected_years)]

a,b,c,d=st.columns(4)
a.metric("Registered Users", f"{users['user_id'].nunique():,}")
b.metric("Active Listeners", f"{listens['user_id'].nunique():,}")
c.metric("Tracks in View", f"{view['track_id'].nunique():,}")
d.metric("Artists in View", f"{view['artist'].nunique():,}")

left,right=st.columns(2)
with left:
    st.subheader("Catalog Genre Composition")
    comp=view.assign(genre=view["genre"].fillna("Unknown")).groupby("genre").size().reset_index(name="tracks").nlargest(12,"tracks")
    fig=px.pie(comp,names="genre",values="tracks",hole=.55)
    st.plotly_chart(style_chart(fig),use_container_width=True)
with right:
    st.subheader("Release Year Distribution")
    years=view.dropna(subset=["year"])
    if years.empty: st.info("Release year data is unavailable for this selection.")
    else:
        fig=px.histogram(years,x="year",nbins=35,labels={"year":"Release year","count":"Tracks"})
        fig.update_traces(marker_color="#1DB954")
        st.plotly_chart(style_chart(fig),use_container_width=True)

st.subheader("Artist Reach vs Playcount")
art=artists.copy()
if selected_genres and "genre" in art: art=art[art["genre"].astype(str).isin(selected_genres)]
fig=px.scatter(art,x="unique_listeners",y="total_playcount",size="total_tracks",hover_name="artist",size_max=32,labels={"unique_listeners":"Unique listeners","total_playcount":"Total playcount","total_tracks":"Catalog tracks"})
fig.update_traces(marker_color="#1DB954",marker_opacity=.72)
st.plotly_chart(style_chart(fig),use_container_width=True)

l,r=st.columns(2)
with l:
    st.subheader("Top Tracks by Unique Listeners")
    top=view.nlargest(15,"unique_listeners").sort_values("unique_listeners")
    fig=px.bar(top,x="unique_listeners",y="name",orientation="h",hover_data=[c for c in ["artist","genre","total_playcount"] if c in top],labels={"unique_listeners":"Unique listeners","name":"Track"})
    fig.update_traces(marker_color="#1DB954")
    st.plotly_chart(style_chart(fig),use_container_width=True)
with r:
    st.subheader("Top Artists by Playcount")
    art_top=artists.nlargest(12,"total_playcount").sort_values("total_playcount")
    fig=px.bar(art_top,x="total_playcount",y="artist",orientation="h",labels={"total_playcount":"Total playcount"})
    fig.update_traces(marker_color="#1DB954")
    st.plotly_chart(style_chart(fig),use_container_width=True)
finish_page()
