import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
# --- LLM setup ---
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

Phong cách trả lời: Chuyên nghiệp, thận trọng, ngắn gọn."""
    ),
    MessagesPlaceholder("history")
])

chain = prompt | llm

# --- Session state for history ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- UI ---
st.title("💊 Drug Info Chatbot")

# Refresh button
if st.button("🔄 Refresh Chat"):
    st.session_state.history = []
    st.rerun()

# Display chat history
for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

# Input box
user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message
    st.chat_message("user").write(user_input)
    st.session_state.history.append(HumanMessage(content=user_input))

    # Get response
    response = chain.invoke({"history": st.session_state.history})
    bot_reply = response.content

    # Show bot message
    st.chat_message("assistant").write(bot_reply)
    st.session_state.history.append(AIMessage(content=bot_reply))

