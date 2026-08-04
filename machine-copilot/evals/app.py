"""Internal QA view of the eval suite — run with:
    streamlit run evals/app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from evals.pipeline import run

st.set_page_config(page_title="Machine Copilot — Eval Dashboard", layout="wide")
st.title("🧪 Machine Copilot — Release Gate")

machine = st.selectbox("Machine model", ["Apex-3200"])

if st.button("Run eval suite", type="primary"):
    with st.spinner("Running golden dataset + guardrail probes..."):
        summary = run(machine)

    gate_pass = summary["release_gate_pass"]
    st.markdown(
        f"## Release gate: {'✅ PASS' if gate_pass else '❌ FAIL'}"
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Cases passed", f"{summary['passed']}/{summary['total_cases']}")
    c2.metric("Guardrail probes blocked", "3/3" if summary["guardrails_all_blocked"] else "FAIL")
    c3.metric("Failed cases", summary["failed"])

    st.subheader("Golden dataset results")
    for case in summary["cases"]:
        icon = "✅" if case["passed"] else "❌"
        with st.expander(f"{icon} [{case['id']}] {case['question']}"):
            st.write("Intent correct:", case["intent_ok"], "→", case["actual_intent"])
            st.write("Source grounded:", case["grounded_ok"], "→", case["citations"])
            st.write("Required terms present:", case["mentions_ok"], "missing:", case["missing_terms"])

    st.subheader("Guardrail safety-bypass probes")
    for probe in summary["guardrail_probes"]:
        icon = "✅ blocked" if probe["blocked"] else "❌ NOT BLOCKED"
        st.write(f"{icon} — \"{probe['probe']}\"")
else:
    st.info("Click 'Run eval suite' to execute the golden dataset + guardrail probes against the current build.")
