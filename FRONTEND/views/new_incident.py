
import streamlit as st

from components import ui
from data.mock_data import EXAMPLE_REPORT
from services import api_client
from utils import validation

ui.page_header(
    "New incident analysis",
    "Submit an incident report to predict root causes, assess risk, and find similar historical incidents."
)

ui.demo_notice()


def _load_example():
    st.session_state["report_text"] = EXAMPLE_REPORT


method = st.radio(
    "How would you like to provide the report?",
    ["Paste report text", "Upload document"],
    horizontal=True
)

text = ""
err = None

if method == "Paste report text":

    st.text_area(
        "Incident report",
        key="report_text",
        height=220,
        placeholder="Describe what happened, when and where, and what caused the incident."
    )

    st.button("Use an example report", on_click=_load_example)

    text = st.session_state.get("report_text", "")

else:

    exts = ", ".join(validation.SUPPORTED_EXTENSIONS)

    uploaded_file = st.file_uploader(
        f"Incident report file ({exts}, up to {validation.MAX_FILE_MB} MB)",
        type=[e.lstrip(".") for e in validation.SUPPORTED_EXTENSIONS]
    )

    if uploaded_file is not None:
        ok, msg, text = validation.validate_upload(
            uploaded_file.name,
            uploaded_file.getvalue()
        )

        if not ok:
            err = msg


if st.button("Analyze incident", type="primary"):

    ok, msg = (
        (False, err)
        if err
        else validation.validate_report_text(text)
    )

    if not ok:
        st.error(msg or "Please provide an incident report.")

    else:
        try:
            with st.status("Analyzing incident...", expanded=True) as status:

                progress = st.empty()

                def on_stage(stage):
                    progress.markdown(f"⏳ {stage}")

                result = api_client.analyze_incident(
                    text,
                    on_stage=on_stage
                )

                status.update(
                    label="Analysis complete",
                    state="complete",
                    expanded=False
                )

            st.session_state["analysis"] = result
            st.switch_page("views/analysis.py")

        except api_client.ApiError as e:
            st.error(str(e))

        except Exception as e:
            st.error(f"Unexpected error: {e}")

elif not text:
    st.info(
        "Paste an incident report or upload a document, then select Analyze incident."
    )
