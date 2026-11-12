import streamlit as st

pages = [
    st.Page("pages/0_Executive_Summary.py", title="Executive Summary", url_path="executive-summary", default=True),
    st.Page("pages/1_Audience_&_Catalog_Insights.py", title="Audience & Catalog Insights", url_path="audience-catalog-insights"),
    st.Page("pages/2_Recommendation_Analytics.py", title="Recommendation Analytics", url_path="recommendation-analytics"),
    st.Page("pages/3_Graph_Analytics_&_Discovery.py", title="Graph Analytics & Discovery", url_path="graph-analytics-discovery"),
]

st.navigation(pages, position="hidden").run()
