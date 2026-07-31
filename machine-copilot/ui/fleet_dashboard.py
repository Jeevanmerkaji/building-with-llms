"""Fleet manager dashboard — plant-manager view: fleet health, predictive
maintenance flags, and usage analytics. This is the Enterprise-tier surface
from the business plan; sold per-site, not per-machine.

Run with: streamlit run ui/fleet_dashboard.py
"""
import streamlit as st
import pandas as pd

from app.telemetry.plc_listener import simulate_stream
from app.telemetry.predictive_signals import analyze_window

st.set_page_config(page_title="Machine Copilot — Fleet Dashboard", layout="wide")
st.title("📊 Fleet Health Dashboard")

FLEET = ["M-101", "M-102", "M-103", "M-104"]
# Simulate one machine trending toward failure so the dashboard has
# something real to flag, mirroring the predictive-maintenance pitch.
WEAR_MACHINE = "M-103"

st.caption(
    "Simulated telemetry for demo purposes — in production this reads live "
    "from each machine's PLC/sensor stream via app/telemetry/plc_listener.py."
)

rows = []
flagged_machines = []
for machine_id in FLEET:
    wear = machine_id == WEAR_MACHINE
    events = list(simulate_stream(machine_id, n_events=40, wear_mode=wear))
    analysis = analyze_window(events)
    status = "⚠️ Needs attention" if analysis["flags"] else "✅ Healthy"
    if analysis["flags"]:
        flagged_machines.append((machine_id, analysis))
    rows.append({
        "Machine": machine_id,
        "Status": status,
        "Alarms (window)": sum(analysis["alarm_counts"].values()),
        "Flags": len(analysis["flags"]),
    })

st.subheader("Fleet overview")
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

if flagged_machines:
    st.subheader("⚠️ Predictive maintenance flags")
    for machine_id, analysis in flagged_machines:
        with st.expander(f"{machine_id} — {len(analysis['flags'])} flag(s)", expanded=True):
            for flag in analysis["flags"]:
                st.markdown(f"**{flag['signal'].replace('_', ' ').title()}**")
                st.write(flag["evidence"])
                st.write("Recommendation:", flag["recommendation"])
                st.caption(f"Reference: {flag['reference']}")
else:
    st.success("No machines currently flagged for predictive maintenance.")

st.subheader("Usage analytics (illustrative)")
usage_df = pd.DataFrame({
    "Machine": FLEET,
    "Copilot queries (7d)": [42, 38, 61, 29],
    "Most common topic": ["Feeds & speeds", "Alarm lookup", "Alarm lookup", "Procedures"],
})
st.dataframe(usage_df, use_container_width=True, hide_index=True)
