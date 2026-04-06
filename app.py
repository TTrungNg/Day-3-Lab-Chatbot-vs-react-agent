"""
Unified entry point — run both Chatbot and ReAct Agent from one place.

    streamlit run app.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, MutableSequence

import streamlit as st
from dotenv import load_dotenv

# Ensure project root is importable.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

# ---------------------------------------------------------------------------
# Page config (must be the very first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Drug Info Assistant", page_icon="💊", layout="centered")

# ---------------------------------------------------------------------------
# Sidebar — mode selector + per-mode settings
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Cài đặt")
    mode = st.radio(
        "Chọn chế độ",
        options=["💬 Chatbot", "🧪 ReAct Agent"],
        index=0,
    )

    if mode == "🧪 ReAct Agent":
        st.divider()
        st.subheader("Cấu hình Agent")
        st.text_input(
            "OpenAI API Key (tùy chọn)",
            type="password",
            key="user_api_key",
            help="Để trống để dùng OPENAI_API_KEY trong file `.env`.",
        )
        _default_model = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
        _model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        _model_idx = _model_options.index(_default_model) if _default_model in _model_options else 0
        selected_model = st.selectbox("Model", options=_model_options, index=_model_idx)
        max_steps = st.slider("Max tool steps", min_value=1, max_value=10, value=5)

    st.divider()
    if st.button("🗑️ Xóa hội thoại"):
        st.session_state.chatbot_history = []
        st.session_state.agent_messages = []
        st.rerun()

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "chatbot_history" not in st.session_state:
    st.session_state.chatbot_history = []

if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

# ---------------------------------------------------------------------------
# CHATBOT mode
# ---------------------------------------------------------------------------
if mode == "💬 Chatbot":
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import HumanMessage, AIMessage

    st.title("💊 Drug Info Chatbot")
    st.caption("Trợ lý tra cứu thuốc — phiên bản Baseline (không dùng tool).")

    @st.cache_resource
    def _build_chatbot_chain():
        llm = ChatGoogleGenerativeAI(model="gemini-flash-latest")
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """Bạn là một "Trợ lý Tra cứu Thuốc & Tương tác Thuốc" phiên bản thử nghiệm (Baseline). 
Mục tiêu của bạn là cung cấp thông tin giáo dục về dược phẩm dựa trên dữ liệu đã học.

CÁC QUY TẮC AN TOÀN BẮT BUỘC:
1. KHÔNG TỰ Ý BỊA ĐẶT: Nếu không chắc chắn 100% về tên thuốc hoặc liều lượng, hãy nói "Tôi không có thông tin chính xác về loại thuốc này".
2. KHÔNG TÍNH TOÁN LIỀU LƯỢNG: Tuyệt đối không thực hiện các phép tính liều lượng theo cân nặng/tuổi cho người dùng. Hãy yêu cầu người dùng hỏi bác sĩ.
3. KHÔNG TRUY CẬP ĐƯỢC DỮ LIỆU THỜI GIAN THỰC: Hãy nhắc người dùng rằng bạn không biết về các loại thuốc mới ra mắt gần đây.
4. ĐIỀU HƯỚNG CHUYÊN GIA: Mọi câu trả lời PHẢI đi kèm lời khuyên: "Vui lòng tham khảo ý kiến của bác sĩ hoặc dược sĩ trước khi sử dụng".
5. CẢNH BÁO TƯƠNG TÁC: Nếu nhận thấy dấu hiệu tương tác nguy hiểm, phải cảnh báo ngay lập tức và yêu cầu người dùng không tự ý kết hợp thuốc.

Phong cách trả lời: Chuyên nghiệp, thận trọng, ngắn gọn.""",
            ),
            MessagesPlaceholder("history"),
        ])
        return prompt | llm

    chain = _build_chatbot_chain()

    for msg in st.session_state.chatbot_history:
        if isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)

    user_input = st.chat_input("Hỏi về thuốc, liều dùng, tương tác...")
    if user_input:
        st.chat_message("user").write(user_input)
        st.session_state.chatbot_history.append(HumanMessage(content=user_input))

        response = chain.invoke({"history": st.session_state.chatbot_history})
        bot_reply = response.content

        st.chat_message("assistant").write(bot_reply)
        st.session_state.chatbot_history.append(AIMessage(content=bot_reply))

# ---------------------------------------------------------------------------
# REACT AGENT mode
# ---------------------------------------------------------------------------
else:
    from src.agent.agent import ReActAgent, default_tools
    from src.core.openai_provider import OpenAIProvider

    st.title("🧪 ReAct Agent Chatbot")
    st.caption("Agent dùng tool thuốc: tra cứu, kiểm tra tương tác, tính liều.")

    def _get_api_key() -> str:
        env_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        ui_key = (st.session_state.get("user_api_key") or "").strip()
        return ui_key or env_key

    def _build_context_prompt(messages: List[dict], current_user_text: str, max_turns: int = 4) -> str:
        recent = messages[-max_turns * 2:] if messages else []
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

    api_key = _get_api_key()
    if not api_key:
        st.warning("Chưa có API key. Thêm `OPENAI_API_KEY` vào `.env` hoặc nhập ở sidebar.")
        st.stop()

    llm = OpenAIProvider(model_name=selected_model, api_key=api_key)
    agent = ReActAgent(llm=llm, tools=default_tools(), max_steps=max_steps)

    for msg in st.session_state.agent_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_text = st.chat_input("Hỏi về thuốc, tương tác, hoặc liều dùng...")
    if user_text:
        st.session_state.agent_messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)

        prompt = _build_context_prompt(st.session_state.agent_messages, current_user_text=user_text)

        with st.chat_message("assistant"):
            try:
                answer = agent.run(prompt)
                st.markdown(answer)
            except Exception as e:
                st.error(f"Lỗi chạy agent: {e}")
                st.session_state.agent_messages.pop()
                st.stop()

        st.session_state.agent_messages.append({"role": "assistant", "content": answer})
