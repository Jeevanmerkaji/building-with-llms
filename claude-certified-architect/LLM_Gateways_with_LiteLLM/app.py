"""
Small Streamlit chat UI in front of the LiteLLM proxy (config.yaml).
Same single-key pattern as gateways.py, just with a browser front end.
"""

import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROXY_URL = os.environ.get("PROXY_URL", "http://localhost:4000")
MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "")
MODELS = ["claude-haiku-4-5", "gpt-4o-mini"]

st.set_page_config(page_title="LiteLLM Gateway Chat")
st.title("LiteLLM Gateway Chat")

client = OpenAI(api_key=MASTER_KEY, base_url=PROXY_URL)

model = st.sidebar.selectbox("Model", MODELS)
st.sidebar.caption(f"Routed through {PROXY_URL}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Ask something...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"Error calling proxy: {e}"
        st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
