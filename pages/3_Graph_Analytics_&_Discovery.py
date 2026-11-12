import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard_common import configure_page, finish_page, load_csv, style_chart

configure_page("Graph Analytics & Discovery", "🕸️")
st.title("Graph Analytics & Discovery")
st.write("Explore the user–track interaction graph and candidate discoveries surfaced by similar listeners.")
try:
    listens=load_csv("listens.csv")
    tracks=load_csv("tracks.csv")
    metrics=load_csv("graph_metrics.csv")
except FileNotFoundError as exc:
    st.error(str(exc)); st.stop()

listens["user_id"]=listens["user_id"].astype(str)
listens["track_id"]=listens["track_id"].astype(str)
tracks["track_id"]=tracks["track_id"].astype(str)
user_degree=listens.groupby("user_id")["track_id"].nunique()
track_degree=listens.groupby("track_id")["user_id"].nunique()
st.subheader("Graph Overview")
a,b,c,d=st.columns(4)
a.metric("Users (nodes)",f"{listens['user_id'].nunique():,}")
b.metric("Tracks (nodes)",f"{tracks['track_id'].nunique():,}")
c.metric("Observed user–track edges",f"{len(listens):,}")
d.metric("Tracks with interactions",f"{track_degree.size:,}")
st.subheader("Provided Graph Metrics")
metric_values=dict(zip(metrics["metric"].astype(str),pd.to_numeric(metrics["value"],errors="coerce")))
metric_rows=[
    ("Connected components", "connected_components", "number"),
    ("Largest component nodes", "largest_component_nodes", "number"),
    ("Average user connections", "average_user_degree", "decimal"),
    ("Average track connections", "average_track_degree", "decimal"),
    ("Maximum track connections", "maximum_track_degree", "number"),
    ("Long-tail tracks", "long_tail_percentage", "percent"),
]
metric_lines=[]
for label,key,kind in metric_rows:
    if key in metric_values and pd.notna(metric_values[key]):
        value=metric_values[key]
        display=f"{value:,.2f}%" if kind=="percent" else f"{value:,.2f}" if kind=="decimal" else f"{value:,.0f}"
        metric_lines.append(f"- **{label}:** {display}")
st.markdown("\n".join(metric_lines))

st.subheader("Most Connected Tracks")
top=track_degree.nlargest(15).rename("unique_listeners").reset_index().merge(tracks,on="track_id",how="left")
top["label"]=top["name"].fillna("Unknown track").astype(str)+" — "+top["artist"].fillna("Unknown artist").astype(str)
fig=px.bar(top.sort_values("unique_listeners"),x="unique_listeners",y="label",orientation="h",labels={"unique_listeners":"Unique listeners","label":"Track"})
fig.update_traces(marker_color="#1DB954")
st.plotly_chart(style_chart(fig),use_container_width=True)

st.subheader("User–Track Network Sample")
st.caption("A sample of the observed network. Nodes represent users and tracks; lines represent listening interactions.")
sample_users=user_degree.nlargest(8).index.astype(str).tolist()
sub=listens[listens["user_id"].isin(sample_users)]
sample_tracks=sub.groupby("track_id")["user_id"].nunique().nlargest(16).index.astype(str).tolist()
sub=sub[sub["track_id"].isin(sample_tracks)].merge(tracks,on="track_id",how="left")
if not sub.empty:
    users=sorted(sub["user_id"].unique())
    tids=sorted(sub["track_id"].unique())
    pos={f"u:{u}":(0,i) for i,u in enumerate(users)}
    pos.update({f"t:{t}":(1,i) for i,t in enumerate(tids)})
    node_ids=list(pos)
    edge_x=[];edge_y=[]
    for row in sub.itertuples(index=False):
        x1,y1=pos[f"u:{row.user_id}"];x2,y2=pos[f"t:{row.track_id}"]
        edge_x.extend([x1,x2,None]);edge_y.extend([y1,y2,None])
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=edge_x,y=edge_y,mode="lines",line=dict(width=1,color="#555"),hoverinfo="skip",showlegend=False))
    uy=[pos[f"u:{u}"][1] for u in users]
    fig.add_trace(go.Scatter(x=[0]*len(users),y=uy,mode="markers+text",name="Users",text=[f"User {u[:8]}" for u in users],textposition="middle left",marker=dict(size=14,color="#1DB954",line=dict(width=1,color="white")),customdata=users,hovertemplate="User %{customdata}<extra></extra>"))
    track_names=sub.drop_duplicates("track_id").set_index("track_id")["name"].fillna("Unknown track").to_dict()
    ty=[pos[f"t:{t}"][1] for t in tids]
    fig.add_trace(go.Scatter(x=[1]*len(tids),y=ty,mode="markers+text",name="Tracks",text=[str(track_names.get(t,"Unknown track"))[:26] for t in tids],textposition="middle right",marker=dict(size=14,color="#b3b3b3",symbol="square",line=dict(width=1,color="white")),customdata=tids,hovertemplate="Track ID %{customdata}<extra></extra>"))
    fig.update_layout(showlegend=True,xaxis=dict(visible=False,range=[-.65,1.65]),yaxis=dict(visible=False),height=max(460,22*max(len(users),len(tids))),margin=dict(l=30,r=30,t=20,b=20))
    st.plotly_chart(style_chart(fig),use_container_width=True)
else: st.info("No interactions available for the selected sample.")

finish_page()
