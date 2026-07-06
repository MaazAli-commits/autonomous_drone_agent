"""
Streamlit dashboard: a simple UI over the FastAPI backend.

This talks to the backend the same way any external client would -- over
HTTP -- rather than importing Python functions directly. That's a
deliberate choice: frontend and backend are separate processes/services,
same as a real deployed system (e.g. a React frontend calling a REST API).
"""

import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Drone Mission Planner")
st.title("Autonomous Drone Mission Planner")
st.write("Describe an inspection mission in plain English, and the agent will plan, fly, and report on it.")

raw_request = st.text_input(
    "Mission request",
    placeholder="e.g. inspect the parking area for unauthorized vehicles",
)

if st.button("Run Mission", type="primary"):
    if not raw_request.strip():
        st.warning("Please enter a mission request first.")
    else:
        with st.spinner("Running mission pipeline (extract → plan → fly → detect → report)..."):
            try:
                response = requests.post(
                    f"{API_URL}/missions/",
                    json={"raw_request": raw_request},
                    timeout=120,  # the full pipeline involves multiple LLM + CV calls, can take a bit
                )
                response.raise_for_status()
                mission = response.json()
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to reach the backend API: {e}")
                st.stop()

        st.success(f"Mission #{mission['id']} completed -- status: {mission['status']}")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Location", mission.get("location") or "unspecified")
        with col2:
            st.metric("Objects detected", len(mission.get("anomalies", [])))

        if mission.get("report"):
            st.subheader("Inspection Report")
            st.write(mission["report"]["summary"])
            st.markdown("**Recommendations:**")
            st.write(mission["report"]["recommendations"])

        if mission.get("anomalies"):
            st.subheader("Detections")
            for a in mission["anomalies"]:
                st.write(f"- **{a['label']}** (confidence: {a['confidence']})")

st.divider()
st.subheader("Past Missions")
try:
    all_missions = requests.get(f"{API_URL}/missions/", timeout=10).json()
    for m in reversed(all_missions):
        with st.expander(f"Mission #{m['id']} — {m['raw_request'][:60]}"):
            st.write(f"Status: {m['status']}")
            if m.get("report"):
                st.write(m["report"]["summary"])
except requests.exceptions.RequestException:
    st.caption("Couldn't load past missions (is the backend running?)")