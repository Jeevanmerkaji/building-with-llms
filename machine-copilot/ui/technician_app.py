"""Technician app — same assistant, framed for a field tech on a tablet:
lets them pick which machine in the shop they're standing in front of, and
surfaces the service-bulletin/procedure angle more prominently than the
operator-facing HMI does.

Run with: streamlit run ui/technician_app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from app.agents.graph import run_query

st.set_page_config(page_title="Machine Copilot — Technician", layout="centered")
st.title("🔧 Technician Assistant")

MACHINES = {
    "M-101 (Apex-3200, Bay 1)": "Apex-3200",
    "M-102 (Apex-3200, Bay 2)": "Apex-3200",
}

machine_label = st.selectbox("Which machine are you working on?", list(MACHINES.keys()))
machine_model = MACHINES[machine_label]

tab1, tab2 = st.tabs(["Ask a question", "Service bulletins"])

with tab1:
    question = st.text_area("Question", placeholder="e.g. What torque should I use for the ball screw retaining nut?")
    if st.button("Ask", type="primary") and question:
        with st.spinner("Searching manuals, alarm tables, and service bulletins..."):
            state = run_query(question, machine_id=machine_label, machine_model=machine_model)
        st.success(state["answer"]) if not state.get("blocked") else st.error(state["answer"])
        if state.get("citations"):
            st.caption("📎 " + ", ".join(state["citations"]))

with tab2:
    st.write("Latest bulletins indexed for this machine model:")
    st.markdown("- **SB-2024-011** — X/Y-Axis Ball Screw Replacement, updated torque spec (28 Nm)")
    st.caption("Ask about a bulletin by number in the 'Ask a question' tab for full detail.")
