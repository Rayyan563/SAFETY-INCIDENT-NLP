import streamlit as st

from components import charts, ui
from services import api_client

ui.page_header("Historical analysis", "Explore history by equipment and see which root causes keep coming back.")
ui.demo_notice()
try:
    df = api_client.list_incidents()
except api_client.ApiError as e:
    st.error(str(e)); st.stop()
if df.empty:
    st.info("No historical incidents are available."); st.stop()

res = st.session_state.get("analysis")
if res:
    ui.section("Compared with your current analysis", f"Incident {res['incident'].get('id', '')}")
    ui.historical_tables(res["historical_analysis"])

ui.section("Equipment history", "What has happened to this equipment before?")
eq = st.selectbox("Equipment", sorted(df["equipment"].unique()))
sub = df[df["equipment"] == eq]
st.caption(f"{len(sub)} incidents, {int((sub['severity'] == 'High').sum())} high severity.")
charts.show(charts.equipment_timeline(sub))
st.dataframe(sub.head(15)[["id", "date", "type", "severity", "root_cause"]], hide_index=True, width="stretch",
             column_config={"id": "Incident ID", "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                            "type": "Type", "severity": "Severity", "root_cause": "Root cause"})

ui.section("Recurring root causes by equipment", "Which equipment and cause combinations repeat?")
charts.show(charts.cause_heatmap(df))
