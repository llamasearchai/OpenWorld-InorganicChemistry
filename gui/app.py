import streamlit as st
from openinorganicchemistry.core.settings import Settings
from openinorganicchemistry.agents.orchestration import run_workflow_sync
from openinorganicchemistry.agents.reporting import generate_report

st.title("OpenInorganicChemistry Dashboard")

s = Settings.load()

input_text = st.text_input("Enter research task")
if st.button("Run Workflow"):
    with st.spinner("Running..."):
        run_id = run_workflow_sync(input_text)
        st.success(f"Workflow completed. Run ID: {run_id}")
        output = st.text_area("Output", height=300, key="output")
        st.write(f"Workflow completed successfully with run ID: {run_id}")

run_id = st.text_input("Enter run_id for report")
if st.button("Generate Report"):
    with st.spinner("Generating..."):
        path = generate_report(run_id)
        st.success(f"Report generated: {path}")
        with open(path, "r") as f:
            st.markdown(f.read())

st.sidebar.title("Settings")
st.sidebar.write(f"Model: {s.model_general}")
if st.sidebar.button("Refresh Settings"):
    st.experimental_rerun()