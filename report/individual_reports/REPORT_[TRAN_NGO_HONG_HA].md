# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Trần Ngô Hồng Hà
- **Student ID**: 2A202600428
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)
P4: QA&Safety Engineer
- Thiết kế các test cases, viết các expected output cho các test case. 
- Thiết kế fallback path, escalation logic
- Chạy thử nghiệm test case và so sánh chatbot vs agent
*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: [none]
- **Code Highlights**: [\src\test_case.md, \src\compilation.md]
- **Documentation**: []

---

## II. Debugging Case Study (10 Points)

**Problem Description**: Agent không xử lý được truy vấn ngoài phạm vi "tính tiền thuốc" (tính giá thuốc), cố gắng gọi tool không tồn tại với tên rỗng, dẫn đến lỗi tool và phản hồi fallback chung chung.
**Log Source**: Snippet từ logs/2026-04-06.log:
{"timestamp": "2026-04-06T09:37:41.726396", "event": "AGENT_START", "data": {"input": "Đây là lịch sử hội thoại gần nhất:\nassistant: Xin lỗi, mình chỉ có thể trả lời trong phạm vi dữ liệu thuốc hiện có của hệ thống (tra cứu thuốc, tương tác thuốc, tính liều).\nuser: tính liều lượng thuốc cho người 15 tuổi, nặng 40kg\nassistant: Liều lượng thuốc paracetamol cho người 15 tuổi, nặng 40kg là khoảng 400-600mg mỗi 4-6 giờ.\nuser: nếu dùng paracetamol với aspirin thì có sao không\nassistant: Dùng paracetamol với aspirin cần phải thận trọng, vì việc sử dụng hai thuốc giảm đau cùng nhau có thể tăng tác dụng phụ và cần được theo dõi. Tôi khuyến nghị bạn nên tham khảo ý kiến bác sĩ hoặc dược sĩ trước khi sử dụng hai loại thuốc này cùng nhau.\nuser: ok cho tôi thuốc\nassistant: Xin lỗi, mình chỉ có thể trả lời trong phạm vi dữ liệu thuốc hiện có của hệ thống (tra cứu thuốc, tương tác thuốc, tính liều).\nuser: tính tiền thuốc\n\nCâu hỏi hiện tại của user:\ntính tiền thuốc", "model": "gpt-4o-mini"}}
[TOOL_CALL] name= args={}
[TOOL_ERROR] name= reason=not_found
[TOOL_OBSERVATION] name= observation={"error": "Tool  not found."}
{"timestamp": "2026-04-06T09:37:45.650444", "event": "AGENT_END", "data": {"steps": 2, "stop_reason": "final"}}
**Diagnosis**: LLM hallucinated việc gọi tool vì input không khớp với tools có sẵn (không có tool tính giá), và prompt hệ thống thiếu xử lý mạnh mẽ cho truy vấn ngoài phạm vi, khiến agent tạo ra action không hợp lệ thay vì fallback an toàn.
**Solution**: Cập nhật prompt hệ thống để bao gồm hướng dẫn fallback rõ ràng cho truy vấn ngoài phạm vi tool, chẳng hạn như "Nếu truy vấn không liên quan đến tra cứu thuốc, kiểm tra tương tác, hoặc tính liều, hãy trả lời lịch sự từ chối và đề xuất hành động liên quan."

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: `Thought` block giúp agent suy luận nhiều bước (multi-stepping reasoning), chọn đúng tool với prompt của user và giúp giảm hallucination so với chatbot trực tiếp
2.  **Reliability**: Trong các trường hợp những câu hỏi đơn giản, không cần suy luận nhiều bước mà chỉ cần trả lời trực tiếp từ base-knowledge, các trường hợp tool trả về output quá phức tạp hoặc bị lỗi, yêu cầu latency thấp. Trong các trường hợp đó, chatbot sẽ tỏ ra có ưu thế hơn so với agent. 
3.  **Observation**: Observation chứa dữ liệu trả về output từ các bước gọi tool, và được đưa vào context window của agent phục vụ cho các bước suy luận tiếp theo. 

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: [e.g., Use an asynchronous queue for tool calls]
- **Safety**: [e.g., Implement a 'Supervisor' LLM to audit the agent's actions]
- **Performance**: [e.g., Vector DB for tool retrieval in a many-tool system]

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
