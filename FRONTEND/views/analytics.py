import pandas as pd
import streamlit as st

from components import charts, ui
from services import api_client

if st.session_state.get("user", {}).get("role") != "analyst":
    st.warning("This page is available to safety analysts."); st.stop()
ui.page_header("Safety analytics", "Aggregate patterns across the incident record.")
ui.demo_notice()
try:
    df = api_client.list_incidents()
except api_client.ApiError as e:
    st.error(str(e)); st.stop()

c = st.columns(2)
months = c[0].selectbox("Period", [6, 12, 24], index=1, format_func=lambda m: f"Last {m} months")
types = c[1].multiselect("Incident type", sorted(df["type"].unique()))
f = df[df["date"] > df["date"].max() - pd.DateOffset(months=months)]
if types: f = f[f["type"].isin(types)]
if f.empty:
    st.info("No incidents match these filters."); st.stop()
st.caption(f"{len(f):,} incidents in view.")

ui.section("Root-cause trend", "Are the leading root causes becoming more or less frequent?")
charts.show(charts.cause_trend_quarterly(f))
ui.section("Severity by root cause", "Which causes lead to the most serious incidents?")
charts.show(charts.severity_by_cause(f))
ui.section("Equipment with repeated high-severity incidents", "Where should follow-up be prioritized?")
t = (f.groupby("equipment").agg(Incidents=("id", "count"), High=("severity", lambda s: int((s == "High").sum())),
                                 Last=("date", "max")).sort_values(["High", "Incidents"], ascending=False).head(10).reset_index())
st.dataframe(t, hide_index=True, width="stretch", column_config={"equipment": "Equipment", "High": "High severity",
             "Last": st.column_config.DateColumn("Most recent", format="YYYY-MM-DD")})
