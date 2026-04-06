"""
Streamlit UI for ReAct Agent (tool-using chatbot).

Run from project root:
    streamlit run src/agent/agent_chatbot.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, MutableSequence

import streamlit as st
from dotenv import load_dotenv

# Ensure project root is importable when running via `streamlit run`.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent.agent import ReActAgent, default_tools
from src.core.openai_provider import OpenAIProvider

load_dotenv()

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")


def _get_api_key() -> str:
    env_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    ui_key = (st.session_state.get("user_api_key") or "").strip()
    return ui_key or env_key


def _build_context_prompt(messages: List[dict], current_user_text: str, max_turns: int = 4) -> str:
    """
    Build a compact context so the ReAct agent can answer coherently across turns.
    """
    recent = messages[-max_turns * 2 :] if messages else []
    context_lines: MutableSequence[str] = []
    for m in recent:
        role = m.get("role", "user")
        content = m.get("content", "")
        context_lines.append(f"{role}: {content}")
    context_block = "\n".join(context_lines).strip()

    if not context_block:
        return current_user_text

    return (
        "Đây là lịch sử hội thoại gần nhất:\n"
        f"{context_block}\n\n"
        "Câu hỏi hiện tại của user:\n"
        f"{current_user_text}"
    )


def main() -> None:
    st.set_page_config(page_title="ReAct Agent Chatbot", page_icon="🧪", layout="centered")

    st.title("ReAct Agent Chatbot")
    st.caption("Agent dùng tool thuốc: tra cứu, kiểm tra tương tác, tính liều.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.subheader("Cấu hình")
        st.text_input(
            "OpenAI API Key (tùy chọn)",
            type="password",
            key="user_api_key",
            help="Để trống để dùng OPENAI_API_KEY trong file `.env`.",
        )
        model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        model_idx = model_options.index(DEFAULT_MODEL) if DEFAULT_MODEL in model_options else 0
        model = st.selectbox("Model", options=model_options, index=model_idx)
        max_steps = st.slider("Max tool steps", min_value=1, max_value=10, value=5)
        if st.button("Xóa hội thoại"):
            st.session_state.messages = []
            st.rerun()

    api_key = _get_api_key()
    if not api_key:
        st.warning("Chưa có API key. Thêm `OPENAI_API_KEY` vào `.env` hoặc nhập ở sidebar.")
        return

    llm = OpenAIProvider(model_name=model, api_key=api_key)
    agent = ReActAgent(llm=llm, tools=default_tools(), max_steps=max_steps)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_text = st.chat_input("Hỏi về thuốc, tương tác, hoặc liều dùng...")
    if not user_text:
        return

    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    prompt = _build_context_prompt(st.session_state.messages, current_user_text=user_text)

    with st.chat_message("assistant"):
        try:
            answer = agent.run(prompt)
            st.markdown(answer)
        except Exception as e:
            st.error(f"Lỗi chạy agent: {e}")
            st.session_state.messages.pop()
            return

    st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()

