# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Tuấn Kiệt
- **Student ID**: 2A202600232
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)


- **Modules Implementated**: [`src/tools/tools.py`],[`src/tools/test_tools.py`],[`src/tools/tools_schema.py`]

- **Code Highlights**: 
  - Mock database definition: [../../src/tools/tools.py](../../src/tools/tools.py#L3-L183) (medicines dictionary with drug information)
  - Drug search function: [../../src/tools/tools.py](../../src/tools/tools.py#L183-L193) (search_drug function for looking up drugs)
  - Check interaction function: [../../src/tools/tools.py](../../src/tools/tools.py#L203-L312) (check_interaction function to check if 2 medicines is dangerous when used together)

- **Documentation**: 

    Thought (LLM): Agent nhận diện yêu cầu và chọn công cụ phù hợp dựa trên mô tả trong tools_schema.md.

    Action (Thực thi): Agent trích xuất tham số và gọi các hàm trong tools.py (search_drug, check_interaction, calculate_dose).

    Observation (Kết quả): Kết quả trả về dưới dạng JSON từ hàm được đưa ngược lại vào Agent để kiểm tra:
    - Tính toán chính xác: Sử dụng Regex để tính liều lượng theo cân nặng thực tế, thay vì để AI tự đoán số.
    - Kiểm tra an toàn: Nếu check_interaction trả về mức độ dangerous, Agent sẽ kích hoạt bước ESCALATE để cảnh báo người dùng.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Agent không xử lý được truy vấn ngoài phạm vi "tính tiền thuốc" (tính giá thuốc), cố gắng gọi tool không tồn tại với tên rỗng, dẫn đến lỗi tool và phản hồi fallback chung chung.
- **Log Source**: Snippet từ `logs/2026-04-06.log`:
  ```
  {"timestamp": "2026-04-06T09:37:41.726396", "event": "AGENT_START", "data": {"input": "Đây là lịch sử hội thoại gần nhất:\nassistant: Xin lỗi, mình chỉ có thể trả lời trong phạm vi dữ liệu thuốc hiện có của hệ thống (tra cứu thuốc, tương tác thuốc, tính liều).\nuser: tính liều lượng thuốc cho người 15 tuổi, nặng 40kg\nassistant: Liều lượng thuốc paracetamol cho người 15 tuổi, nặng 40kg là khoảng 400-600mg mỗi 4-6 giờ.\nuser: nếu dùng paracetamol với aspirin thì có sao không\nassistant: Dùng paracetamol với aspirin cần phải thận trọng, vì việc sử dụng hai thuốc giảm đau cùng nhau có thể tăng tác dụng phụ và cần được theo dõi. Tôi khuyến nghị bạn nên tham khảo ý kiến bác sĩ hoặc dược sĩ trước khi sử dụng hai loại thuốc này cùng nhau.\nuser: ok cho tôi thuốc\nassistant: Xin lỗi, mình chỉ có thể trả lời trong phạm vi dữ liệu thuốc hiện có của hệ thống (tra cứu thuốc, tương tác thuốc, tính liều).\nuser: tính tiền thuốc\n\nCâu hỏi hiện tại của user:\ntính tiền thuốc", "model": "gpt-4o-mini"}}
  [TOOL_CALL] name= args={}
  [TOOL_ERROR] name= reason=not_found
  [TOOL_OBSERVATION] name= observation={"error": "Tool  not found."}
  {"timestamp": "2026-04-06T09:37:45.650444", "event": "AGENT_END", "data": {"steps": 2, "stop_reason": "final"}}
  ```
- **Diagnosis**: LLM hallucinated việc gọi tool vì input không khớp với tools có sẵn (không có tool tính giá), và prompt hệ thống thiếu xử lý mạnh mẽ cho truy vấn ngoài phạm vi, khiến agent tạo ra action không hợp lệ thay vì fallback an toàn.
- **Solution**: Cập nhật prompt hệ thống để bao gồm hướng dẫn fallback rõ ràng cho truy vấn ngoài phạm vi tool, chẳng hạn như "Nếu truy vấn không liên quan đến tra cứu thuốc, kiểm tra tương tác, hoặc tính liều, hãy trả lời lịch sự từ chối và đề xuất hành động liên quan."

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: Với `Thought`, ReAct buộc agent phải tự tóm tắt bước suy luận trước khi gọi công cụ. Điều này giúp tách biệt “ý định” và “hành động”, giảm thiểu việc LLM trả lời trực tiếp mà không dùng tool. So với Chatbot baseline chỉ dựa vào prompt và history, agent có cấu trúc rõ ràng hơn: nếu cần kiểm tra tương tác thuốc, nó sẽ suy nghĩ “Tôi cần kiểm tra tương tác” rồi mới thực hiện `Action: check_interaction(...)`.

2.  **Reliability**: Agent hoạt động tốt hơn khi yêu cầu rõ ràng cần dùng tool, ví dụ “kiểm tra tương tác thuốc A và B” hoặc “tính liều theo cân nặng”. Nhưng trong một số trường hợp, agent có thể kém hơn Chatbot:
    - Nếu hệ thống phân tích `Action`/`Observation` chưa triển khai đầy đủ, agent dễ bị kẹt do parse sai hoặc vòng lặp không dừng.
    - Nếu tool spec không rõ ràng, agent có thể cố gắng gọi tool không cần thiết, trong khi Chatbot chỉ trả lời đơn thuần.
    - Với các câu hỏi đơn giản không cần thao tác tool, Chatbot thường trả lời nhanh và liền mạch hơn.

3.  **Observation**: `Observation` là phản hồi từ công cụ nên môi trường feedback bắt buộc agent cập nhật thông tin liên tục. Ví dụ nếu `check_interaction` trả về “dangerous”, agent sẽ dùng observation đó để chuyển sang cảnh báo và không tiếp tục tính liều hoặc trả lời lạc đề. Nếu tool trả về “no interaction”, agent có thể tiếp tục với bước tiếp theo như “tính liều” hoặc “đưa ra kết luận”.

> Kết luận: ReAct mạnh ở chỗ quản lý suy luận từng bước và đánh giá kết quả tool, còn Chatbot đơn giản phù hợp với các câu hỏi trực tiếp. Giá trị của agent nằm ở khả năng dùng `Thought` + `Action` + `Observation` để tự điều chỉnh và giảm hallucination khi cần công cụ đặc thù.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Sử dụng hàng đợi bất đồng bộ (asynchronous queue) cho các cuộc gọi tool để xử lý đồng thời nhiều yêu cầu và giảm độ trễ khi model chờ tool phản hồi. Xây dựng kiến trúc microservice cho từng tool để dễ mở rộng và bảo trì.
- **Safety**: Triển khai một lớp giám sát `Supervisor LLM` để audit lại các action của agent trước khi thực thi, đồng thời thêm cơ chế kiểm tra an toàn (safety filter) cho mọi kết quả tool. Đặt giới hạn `max_steps` và kiểm soát vòng lặp để tránh agent chạy quá lâu hoặc lặp vô hạn.
- **Performance**: Sử dụng cache/secondary store cho kết quả tool phổ biến và lưu trữ observation lịch sử để giảm số lần gọi lặp. Với nhiều tool, dùng vector database để tìm kiếm tool phù hợp dựa trên intent và schema, giúp agent chọn chính xác tool nhanh hơn.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
