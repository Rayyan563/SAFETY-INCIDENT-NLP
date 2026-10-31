import math

import streamlit as st

from components import ui
from services import api_client

ui.page_header("Incident history", "Search and filter past incidents.")
ui.demo_notice()
try:
    df = api_client.list_incidents()
except api_client.ApiError as e:
    st.error(str(e)); st.stop()
if df.empty:
    ui.empty_state("No incidents yet", "Analyzed incidents will appear here.", "views/new_incident.py", "New incident"); st.stop()

KEYS = ["h_q", "h_dates", "h_type", "h_sev", "h_cause", "h_eq"]
def _reset():
    for k in KEYS:
        st.session_state.pop(k, None)

r1 = st.columns([2, 1.4])
q = r1[0].text_input("Search ID or keywords", key="h_q")
dates = r1[1].date_input("Date range", value=(df["date"].min().date(), df["date"].max().date()), key="h_dates")
r2 = st.columns(4)
types = r2[0].multiselect("Incident type", sorted(df["type"].unique()), key="h_type")
sevs = r2[1].multiselect("Severity", ["Low", "Medium", "High"], key="h_sev")
causes = r2[2].multiselect("Root cause", sorted(df["root_cause"].unique()), key="h_cause")
eqs = r2[3].multiselect("Equipment", sorted(df["equipment"].unique()), key="h_eq")

f = df
if q: f = f[f["id"].str.contains(q, case=False) | f["summary"].str.contains(q, case=False)]
if isinstance(dates, tuple) and len(dates) == 2:
    f = f[(f["date"].dt.date >= dates[0]) & (f["date"].dt.date <= dates[1])]
for col, vals in [("type", types), ("severity", sevs), ("root_cause", causes), ("equipment", eqs)]:
    if vals: f = f[f[col].isin(vals)]
active = sum(bool(v) for v in (q, types, sevs, causes, eqs))
cap, btn = st.columns([4, 1])
cap.caption(f"{len(f):,} of {len(df):,} incidents" + (f", {active} filter(s) active" if active else ""))
btn.button("Reset filters", on_click=_reset)

if f.empty:
    st.info("No incidents match these filters. Reset or widen them."); st.stop()
size = 25
pages = math.ceil(len(f) / size)
page = st.number_input("Page", 1, pages, 1) if pages > 1 else 1
view = f.iloc[(page - 1) * size: page * size][["id", "date", "type", "equipment", "severity", "root_cause"]].reset_index(drop=True)
ev = st.dataframe(view, hide_index=True, width="stretch", on_select="rerun", selection_mode="single-row", key="h_table",
                  column_config={"id": "Incident ID", "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"), "type": "Type",
                                 "equipment": "Equipment", "severity": "Severity", "root_cause": "Root cause"})
sel = ev.selection.rows
if sel:
    iid = view.iloc[sel[0]]["id"]
    if st.button(f"Open analysis for {iid}", type="primary"):
        try:
            st.session_state["analysis"] = api_client.get_incident_analysis(iid)
            st.switch_page("views/analysis.py")
        except api_client.ApiError as e:
            st.error(str(e))
else:
    st.caption("Select a row to open its analysis. Click a column header to sort.")
