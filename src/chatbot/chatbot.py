import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from src.tools.tools import check_interaction, medicines
from src.telemetry.logger import logger

load_dotenv()
# --- LLM setup ---
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    google_api_key=os.getenv("GEMINI_API_KEY")
)
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

# --- Escalation helpers ---

def _build_category_to_drug_map():
    """Build a reverse map: category name (lowercase) -> first drug of that category."""
    mapping = {}
    for drug_name, data in medicines.items():
        cat = data.get("category") or data.get("loại_thuốc")
        if cat and cat.lower() not in mapping:
            mapping[cat.lower()] = drug_name
    return mapping

_CATEGORY_TO_DRUG = _build_category_to_drug_map()

def _detect_drug_pair(text: str):
    """
    Scan text for two known drug names OR category names.
    Returns (drug1, drug2) or None.
    """
    text_lower = text.lower()

    # 1. Try matching exact drug names first
    found = [name for name in medicines if name.lower() in text_lower]
    if len(found) >= 2:
        return (found[0], found[1])

    # 2. Try matching category names -> map to representative drug
    found_via_category = []
    for cat_lower, drug_name in _CATEGORY_TO_DRUG.items():
        if cat_lower in text_lower and drug_name not in found_via_category:
            found_via_category.append(drug_name)
        if len(found_via_category) == 2:
            break

    # 3. Mix: one drug name + one category
    if len(found) == 1 and len(found_via_category) >= 1:
        candidate = found_via_category[0]
        if candidate != found[0]:
            return (found[0], candidate)

    if len(found_via_category) >= 2:
        return (found_via_category[0], found_via_category[1])

    return None

def handle_escalation(user_input: str):
    """
    If user message contains two known drug names, call check_interaction and return
    (bot_reply, is_escalated). Returns (None, False) when not applicable.
    """
    drug_pair = _detect_drug_pair(user_input)
    if not drug_pair:
        return None, False

    drug1, drug2 = drug_pair
    result = check_interaction(drug1, drug2)

    if result.get("interaction") == "dangerous":
        # TRUE case: dangerous interaction
        logger.log_escalation(drug1, drug2, result.get("message", ""))
        reply = (
            f"⚠️ **CẢNH BÁO TƯƠNG TÁC THUỐC NGUY HIỂM** [ESCALATE]\n\n"
            f"{result['message']}\n\n"
            f"**Khuyến nghị:** Vui lòng tham khảo ý kiến bác sĩ trực tiếp trước khi sử dụng "
            f"đồng thời **{drug1}** và **{drug2}**."
        )
        return reply, True
    else:
        # FALSE case: no dangerous interaction
        reply = (
            f"Hiện không có thông tin nào về các tương tác nguy hiểm giữa {drug1} và {drug2}. "
            f"Bạn có thể sử dụng an toàn.\n\n"
            f"Lưu ý: nếu xảy ra bất kỳ triệu chứng bất thường nào sau khi sử dụng thuốc, "
            f"ngay lập tức đến các cơ sở y tế để được thăm khám và điều trị kịp thời."
        )
        return reply, False

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

    # --- Escalation check (takes priority over LLM) ---
    escalation_reply, is_escalated = handle_escalation(user_input)

    if escalation_reply:
        bot_reply = escalation_reply
        if is_escalated:
            st.error(bot_reply)
        else:
            st.chat_message("assistant").write(bot_reply)
    else:
        # Normal LLM path
        response = chain.invoke({"history": st.session_state.history})
        bot_reply = response.content if isinstance(response.content, str) else response.content[0]["text"]
        st.chat_message("assistant").write(bot_reply)

    st.session_state.history.append(AIMessage(content=bot_reply))

