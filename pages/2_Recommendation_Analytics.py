import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_common import configure_page, finish_page, load_csv, style_chart, spotify_table

configure_page("Recommendation Analytics", "✨")
st.title("Recommendation Analytics")
st.write("Explore ALS ranking quality, recommendation reach, and user-level recommendations.")
try:
    summary=load_csv("recommendation_analytics.csv")
    ranks=load_csv("recommendation_rank_analytics.csv")
    coverage=load_csv("recommendation_coverage.csv")
    recommendations=load_csv("als_recommendations.csv")
    metrics=load_csv("als_metrics.csv")
except FileNotFoundError as exc:
    st.error(str(exc)); st.stop()

metric_map=dict(zip(metrics["metric"].astype(str).str.lower(),pd.to_numeric(metrics["value"],errors="coerce")))
def metric_value(name):
    return next((v for k,v in metric_map.items() if name in k),None)
coverage_map=dict(zip(coverage["metric"].astype(str).str.lower(),pd.to_numeric(coverage["value"],errors="coerce")))
cover=next((v for k,v in coverage_map.items() if "coverage" in k),None)
with st.container(key="compact_recommendation_metrics"):
    metric_cols=st.columns(5)
    for col,label,key in zip(metric_cols,["Recall@5","Recall@10","Recall@20","Recall@50","NDCG@10"],["recall@5","recall@10","recall@20","recall@50","ndcg@10"]):
        val=metric_value(key)
        col.metric(label,f"{val:.2%}" if val is not None and pd.notna(val) else "—")

summary["genre"]=summary["genre"].fillna("Unknown")
st.subheader("Recommendation Reach")
x,y,z=st.columns(3)
x.metric("Recommendation Rows",f"{len(recommendations):,}")
y.metric("Unique Recommended Tracks",f"{recommendations['track_id'].nunique():,}")
z.metric("Catalog Coverage",f"{cover:.2f}%" if cover is not None and pd.notna(cover) else "—")

l,r=st.columns(2)
with l:
    st.markdown("#### Recommendation Genre Mix")
    fig=px.pie(summary,names="genre",values="recommendation_count",hole=.55)
    st.plotly_chart(style_chart(fig),use_container_width=True)
with r:
    st.markdown("#### ALS Model Score by Rank")
    if "avg_als_score" in ranks:
        fig=px.line(ranks.sort_values("rank"),x="rank",y="avg_als_score",markers=True,labels={"rank":"Recommendation rank","avg_als_score":"Mean ALS model score"})
        fig.update_traces(line_color="#1DB954",marker_color="#1DB954")
        st.plotly_chart(style_chart(fig),use_container_width=True)
    else: st.info("Rank level score data is unavailable.")
st.subheader("Top Recommended Tracks")
top=recommendations.groupby(["track_id","name","artist","genre"],dropna=False).agg(recommendation_frequency=("user_id","nunique"),mean_als_score=("als_score","mean")).reset_index().nlargest(15,"recommendation_frequency").sort_values("recommendation_frequency")
fig=px.bar(top,x="recommendation_frequency",y="name",orientation="h",hover_data=["artist","genre","mean_als_score"],labels={"recommendation_frequency":"Users recommended","name":"Track","mean_als_score":"Mean ALS model score"})
fig.update_traces(marker_color="#1DB954")
st.plotly_chart(style_chart(fig),use_container_width=True)

st.subheader("User-level Recommendations")
user_ids=sorted(recommendations["user_id"].dropna().astype(str).unique())
if user_ids:
    user_id=st.selectbox("user_id",user_ids,key="rec_user_select")
    user_recs=recommendations[recommendations["user_id"].astype(str)==user_id].sort_values("rank")
    fields=[c for c in ["rank","name","artist","genre","year","als_score"] if c in user_recs]
    display_recs=user_recs[fields].copy()
    if "genre" in display_recs:
        display_recs["genre"]=display_recs["genre"].replace({None:"-","None":"-"}).fillna("-")
    display_recs=display_recs.rename(columns={"rank":"Rank","name":"Track","artist":"Artist","genre":"Genre","year":"Year","als_score":"ALS Score"})
    st.markdown(spotify_table(display_recs).hide(axis="index").to_html(),unsafe_allow_html=True)
else: st.info("No user-level recommendations are available.")
finish_page()
