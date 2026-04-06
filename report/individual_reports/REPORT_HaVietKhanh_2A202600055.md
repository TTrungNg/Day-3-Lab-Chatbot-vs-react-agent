# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Hà Việt Khánh
- **Student ID**: 2A202600055
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

Tôi đã thực hiện một loạt các cải tiến quan trọng cho hệ thống ReAct Agent để tăng tính ổn định, trải nghiệm người dùng và khả năng xử lý ngữ cảnh thông minh.

- **Modules Implementated**: 
    - `src/tools/tools.py`: Nâng cấp hàm `search_drug`, `calculate_dose` và `check_interaction`.
    - `src/agent/agent.py`: Cải thiện logic `ReActAgent`, `_safety_check` và bộ lọc `_has_grounded_data`.
    - `src/agent/agent_chatbot.py`: Fix lỗi hiển thị và xử lý lịch sử hội thoại.

- **Code Highlights**:
    - **Fuzzy Search (Gợi ý thuốc)**: Sử dụng `difflib.get_close_matches` để gợi ý tên thuốc khi người dùng nhập sai (ví dụ: "Apirin" -> "Aspirin").
    - **Category-based Interaction**: Cho phép kiểm tra tương tác giữa các **nhóm thuốc** (ví dụ: "Kháng sinh" và "Thuốc chống đông máu") thay vì chỉ tên thuốc cụ thể.
    - **Anti-hallucination Prompting**: Thêm chỉ dẫn cứng vào Tool Schema: `"KHÔNG ĐƯỢC TỰ ĐOÁN cân nặng và tuổi. Nếu user chưa cung cấp thì phải truyền vào 0."` giúp ngăn chặn việc LLM tự bịa số liệu.

- **Documentation**: Code của tôi giúp Agent tương tác mượt mà hơn với vòng lặp ReAct. Khi thiếu thông tin (như cân nặng), thay vì báo lỗi hệ thống, Tool sẽ trả về một `message` thân thiện. Tôi đã điều chỉnh `_safety_check` để cho phép các câu hỏi làm rõ này đi qua bộ lọc an toàn, giúp Agent có thể chủ động hỏi lại người dùng.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: Khi người dùng hỏi "Tính liều lượng cho tôi" sau khi đã được giới thiệu tên thuốc ở câu trước, Agent trả về câu từ chối mặc định: *"Xin lỗi, mình chỉ có thể trả lời trong phạm vi dữ liệu..."* mặc dù dữ liệu thuốc đã được tra cứu.
- **Diagnosis**: 
    1. **Vấn đề an toàn**: Hàm `_safety_check` quá khắt khe, nó chặn mọi câu trả lời của Agent nếu `observations` trống (xảy ra khi Agent chỉ muốn hỏi lại người dùng thông tin còn thiếu mà chưa gọi Tool).
    2. **Mất ngữ cảnh**: Lịch sử hội thoại bị trùng lặp trong Prompt khiến Model bị nhiễu và không trích xuất được tên thuốc từ câu trước.
- **Solution**: 
    1. Sửa `_has_grounded_data` để chấp nhận các "Soft Observation" (tin nhắn hướng dẫn từ Tool).
    2. Cập nhật `_safety_check` bằng Regex và từ khóa để nhận diện các câu hỏi làm rõ (chứa "?", "bao nhiêu", "vui lòng...").
    3. Fix hàm `_build_context_prompt` trong UI để loại bỏ tin nhắn trùng lặp.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1.  **Reasoning**: Khối `Thought/Reason` giúp Agent "nghĩ trước khi làm". Ví dụ, Agent nhận ra: *"Tôi có tên thuốc từ lịch sử nhưng thiếu cân nặng, tôi nên hỏi người dùng thay vì gọi hàm tính toán sai."* Điều này vượt xa một Chatbot thông thường chỉ trả lời dựa trên văn bản.
2.  **Reliability**: Agent đôi khi hoạt động kém hơn khi gặp các mô hình LLM quá "lanh chanh" (như GPT-4o-mini). Nó cố gắng tự điền các tham số mặc định (như 70kg, 30 tuổi) vào Tool thay vì hỏi lại, dẫn đến kết quả tính toán có thể gây nguy hiểm nếu người dùng không chú ý.
3.  **Observation**: Phản hồi từ môi trường (Observation) đóng vai trò là "Ground Truth". Nếu Tool báo "Không tìm thấy thuốc", Agent sẽ ngay lập tức thay đổi chiến thuật sang gợi ý thuốc gần đúng, thay vì cố gắng bịa ra thông tin không có thật.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Triển khai hệ thống lưu trữ Vector DB (như Pinecone/ChromaDB) để lưu trữ hàng nghìn loại thuốc thật, thay vì dùng Mock DB tĩnh như hiện tại.
- **Safety**: Xây dựng một lớp "Guardrail" độc lập để kiểm tra logic liều lượng một lần nữa bằng các công thức y khoa cứng (tĩnh) trước khi hiển thị cho người dùng, tránh hoàn toàn rủi ro từ LLM.
- **Performance**: Chuyển sang mô hình Function Calling (Native Tool Use) của OpenAI thay vì dùng Parser Regex để tăng độ chính xác khi trích xuất tham số JSON từ Action.

---