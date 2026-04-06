"""
Simple chatbot UI (Streamlit) using the OpenAI Chat Completions API with streaming.

Run from project root:
    streamlit run src/chatbot/chatbot.py

Set OPENAI_API_KEY in `.env` (see `.env.example`) or paste a key in the sidebar.
"""

from __future__ import annotations

import os
from typing import Generator, List, MutableSequence

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")


def _get_api_key() -> str:
    env_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    ui_key = (st.session_state.get("user_api_key") or "").strip()
    return ui_key or env_key


def _openai_stream(
    client: OpenAI,
    model: str,
    messages: List[dict],
) -> Generator[str, None, None]:
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def main() -> None:
    st.set_page_config(page_title="Chatbot (OpenAI)", page_icon="💬", layout="centered")

    st.title("Chatbot")
    st.caption("Baseline: một LLM thuần, không công cụ — so sánh với ReAct agent.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.subheader("Cấu hình")
        st.text_input(
            "OpenAI API Key (tùy chọn)",
            type="password",
            key="user_api_key",
            help="Để trống để dùng biến OPENAI_API_KEY trong file `.env`.",
        )
        model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        model_idx = (
            model_options.index(DEFAULT_MODEL)
            if DEFAULT_MODEL in model_options
            else 0
        )
        model = st.selectbox("Model", options=model_options, index=model_idx)
        if st.button("Xóa hội thoại"):
            st.session_state.messages = []
            st.rerun()

    api_key = _get_api_key()
    if not api_key:
        st.warning(
            "Chưa có API key. Thêm `OPENAI_API_KEY` vào `.env` hoặc nhập ở sidebar."
        )
        return

    client = OpenAI(api_key=api_key)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_text = st.chat_input("Nhập tin nhắn...")
    if not user_text:
        return

    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    messages: MutableSequence[dict] = [
        {
            "role": "system",
            "content": """Bạn là một "Trợ lý Tra cứu Thuốc & Tương tác Thuốc" phiên bản thử nghiệm (Baseline). 
Mục tiêu của bạn là cung cấp thông tin giáo dục về dược phẩm dựa trên dữ liệu đã học.

CÁC QUY TẮC AN TOÀN BẮT BUỘC:
1. KHÔNG TỰ Ý BỊA ĐẶT: Nếu không chắc chắn 100% về tên thuốc hoặc liều lượng, hãy nói "Tôi không có thông tin chính xác về loại thuốc này".
2. KHÔNG TÍNH TOÁN LIỀU LƯỢNG: Tuyệt đối không thực hiện các phép tính liều lượng theo cân nặng/tuổi cho người dùng. Hãy yêu cầu người dùng hỏi bác sĩ.
3. KHÔNG TRUY CẬP ĐƯỢC DỮ LIỆU THỜI GIAN THỰC: Hãy nhắc người dùng rằng bạn không biết về các loại thuốc mới ra mắt gần đây.
4. ĐIỀU HƯỚNG CHUYÊN GIA: Mọi câu trả lời PHẢI đi kèm lời khuyên: "Vui lòng tham khảo ý kiến của bác sĩ hoặc dược sĩ trước khi sử dụng".
5. CẢNH BÁO TƯƠNG TÁC: Nếu nhận thấy dấu hiệu tương tác nguy hiểm, phải cảnh báo ngay lập tức và yêu cầu người dùng không tự ý kết hợp thuốc.

Phong cách trả lời: Chuyên nghiệp, thận trọng, ngắn gọn.""",
        },
        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
    ]

    with st.chat_message("assistant"):
        try:
            full = st.write_stream(_openai_stream(client, model, list(messages)))
        except Exception as e:
            st.error(f"Lỗi gọi OpenAI: {e}")
            st.session_state.messages.pop()
            return

    st.session_state.messages.append({"role": "assistant", "content": full or ""})


if __name__ == "__main__":
    main()
