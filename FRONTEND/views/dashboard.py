import pandas as pd
import streamlit as st

from components import charts, ui
from services import api_client

ui.page_header("Dashboard", "What is happening overall, and what deserves a closer look.")
ui.demo_notice()
try:
    df = api_client.list_incidents()
except api_client.ApiError as e:
    st.error(str(e)); st.stop()
if df.empty:
    ui.empty_state("No incidents yet", "Analyze your first incident report to start building history.", "views/new_incident.py", "New incident"); st.stop()

end = df["date"].max()
last, prev = df[df["date"] > end - pd.Timedelta(days=90)], df[(df["date"] <= end - pd.Timedelta(days=90)) & (df["date"] > end - pd.Timedelta(days=180))]
high = df[df["severity"] == "High"]
yr_high = high[high["date"] > end - pd.Timedelta(days=365)]["equipment"].value_counts()
c = st.columns(4)
with c[0]: ui.metric_card("Incidents on record", f"{len(df):,}")
with c[1]: ui.metric_card("High severity", f"{len(high):,}", f"{len(high) / len(df):.0%} of all incidents")
with c[2]: ui.metric_card("Last 90 days", f"{len(last):,}", f"{len(last) - len(prev):+d} vs the previous 90 days")
with c[3]: ui.metric_card("Most high-severity incidents, past year", yr_high.index[0] if len(yr_high) else "None", f"{yr_high.iloc[0]} incidents" if len(yr_high) else None)

ui.section("Incident trend", "Is the number of incidents, and of serious ones, rising or falling?")
charts.show(charts.monthly_trend(df))
a, b = st.columns(2)
with a:
    ui.section("Recurring root causes", "Which causes appear most often?")
    charts.show(charts.category_bar(df, "root_cause", "Root cause"))
with b:
    ui.section("Equipment patterns", "Which equipment is involved most often?")
    charts.show(charts.category_bar(df, "equipment", "Equipment"))
a, b = st.columns([1, 1.3])
with a:
    ui.section("Incident types", "What kinds of incidents occur?")
    charts.show(charts.category_bar(df, "type", "Incident type", top=6))
with b:
    ui.section("Recent incidents")
    st.dataframe(df.head(8)[["id", "date", "type", "equipment", "severity"]], hide_index=True, width="stretch",
                 column_config={"id": "Incident ID", "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                                "type": "Type", "equipment": "Equipment", "severity": "Severity"})
