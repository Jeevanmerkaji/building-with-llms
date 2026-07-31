"""Shop-floor HMI chat — designed for a touchscreen kiosk mounted on the
machine controller. Large tap targets, minimal typing, big text.

Run with: streamlit run ui/hmi_chat.py
"""
import streamlit as st
from app.agents.graph import run_query
from app.config import settings

st.set_page_config(page_title="Machine Copilot", layout="centered")

st.markdown(
    """
    <style>
    .stButton button { font-size: 20px; padding: 0.75em 1.5em; }
    .stChatMessage { font-size: 18px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title(f"🛠️ Machine Copilot — {settings.machine_model}")
st.caption("Ask about alarms, feeds & speeds, or maintenance procedures.")

if "history" not in st.session_state:
    st.session_state.history = []

QUICK_PROMPTS = [
    "What should I check for alarm ALM-4021?",
    "Feed rate for 6061 aluminum, 10mm endmill?",
    "How do I replace the ball screw?",
]

cols = st.columns(len(QUICK_PROMPTS))
quick_pick = None
for col, prompt in zip(cols, QUICK_PROMPTS):
    if col.button(prompt):
        quick_pick = prompt

for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.write(turn["content"])
        if turn.get("citations"):
            st.caption("📎 Source: " + ", ".join(turn["citations"]))

user_input = st.chat_input("Type your question...") or quick_pick

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Checking manuals and alarm tables..."):
            state = run_query(user_input, machine_id="HMI-01", machine_model=settings.machine_model)
        st.write(state["answer"])
        if state.get("citations"):
            st.caption("📎 Source: " + ", ".join(state["citations"]))
        st.session_state.history.append({
            "role": "assistant",
            "content": state["answer"],
            "citations": state.get("citations", []),
        })
