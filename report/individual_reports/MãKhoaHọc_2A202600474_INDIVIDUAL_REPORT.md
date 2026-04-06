# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Mã Khoa Học
- **Student ID**: 2A202600474
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

Trong buổi lab này, tôi tập trung xây dựng hoàn chỉnh luồng ReAct Agent có khả năng gọi tool thật, nhận observation và sinh câu trả lời có kiểm soát phạm vi.

- **Modules Implementated**:
  - `src/agent/agent.py`: hoàn thiện ReAct core loop (Reason -> Action -> Observation -> lặp -> Final Answer -> Safety Check), parser `Action`, thực thi tool động, domain guard, safety guard, log tool call.
  - `src/agent/run_agent.py`: CLI để chạy agent tương tác trực tiếp với OpenAI/Gemini/Local provider.
  - `src/agent/agent_chatbot.py`: UI Streamlit cho agent dựa trên giao diện baseline chatbot.
  - `src/tools/tools.py`: sửa lỗi tính liều với dữ liệu localized (`name`/`tên`) cho thuốc như `Aficamten`.

- **Code Highlights**:
  - Agent parse được 2 format action:
    - `Action: {"tool":"...","args":{...}}`
    - `Action: tool_name({...})`
  - Tool registry chuẩn hóa bằng `default_tools()` với `name`, `description`, `args_schema`, `func`.
  - Agent có cơ chế fallback an toàn:
    - Có lỗi tool => trả thông báo lỗi truy xuất dữ liệu (không nhầm sang “ngoài phạm vi”).
    - Không có grounded observation => từ chối trả lời ngoài phạm vi data thuốc.
    - Có `interaction == dangerous` => cảnh báo an toàn và khuyến nghị liên hệ chuyên gia y tế.
  - Logging thêm trong terminal:
    - `[TOOL_CALL]`
    - `[TOOL_OBSERVATION]`
    - `[TOOL_ERROR]`

- **Documentation**:
  - Sử dụng schema mô tả tool từ `src/tools/tools_schema.md` để align input/output giữa agent và tool layer.
  - Bổ sung hướng dẫn chạy thực tế:
    - CLI: `python -m src.agent.run_agent --provider openai --model gpt-4o-mini`
    - Streamlit: `streamlit run src/agent/agent_chatbot.py`

---

## II. Debugging Case Study (10 Points)

- **Problem Description**:
  Agent trả về: “Xin lỗi, mình chỉ có thể trả lời trong phạm vi dữ liệu...” cho câu hỏi vẫn thuộc domain:  
  `tính liều cho Aficamten cho người 17 tuổi 50 kg`.

- **Log Source**:
  Từ log terminal:
  - `[TOOL_CALL] name=calculate_dose args={'drug_name': 'Aficamten', 'weight_kg': 50, 'age_years': 17}`
  - `[TOOL_ERROR] name=calculate_dose reason='name'`
  - `[TOOL_OBSERVATION] ... {"error": "Tool call failed: 'name'"}`

- **Diagnosis**:
  Root cause nằm ở tool layer, không phải do model:
  - `calculate_dose()` truy cập `med["name"]`.
  - Một số bản ghi thuốc mới dùng key localized `tên` thay vì `name`.
  - Gây `KeyError('name')`, làm agent nhận observation lỗi và kích hoạt nhánh fallback.

- **Solution**:
  - Sửa `calculate_dose()` dùng `_get_med_field(med, "name", "tên")` thay vì hard-code `med["name"]`.
  - Sửa hậu kiểm agent:
    - Nếu có tool error -> thông báo lỗi truy xuất dữ liệu.
    - Chỉ dùng thông báo “ngoài phạm vi” khi thật sự không có grounded data.
  - Bổ sung test regression:
    - `test_calculate_dose_localized_entry` trong `src/tools/test_tools.py`.
  - Chuyển log observation sang ASCII-safe để tránh `UnicodeEncodeError` trên Windows terminal.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**:
   ReAct tốt hơn chatbot thuần trong bài toán cần dữ liệu có cấu trúc, vì nó tách rõ:
   - suy luận cần thông tin gì,
   - gọi tool nào,
   - dùng observation để trả lời.
   Chatbot thuần dễ trả lời “trơn tru” nhưng không đảm bảo grounded theo dữ liệu thật.

2. **Reliability**:
   Agent có thể tệ hơn chatbot khi:
   - parser action fail,
   - tool schema chưa rõ,
   - dữ liệu không đồng nhất field (`name` vs `tên`),
   - hoặc tool runtime lỗi.
   Khi đó chatbot thuần có thể vẫn trả lời được (nhưng không đáng tin bằng).

3. **Observation**:
   Observation là cơ chế feedback quan trọng nhất:
   - Nếu observation đúng và đầy đủ -> agent trả lời chính xác, có căn cứ.
   - Nếu observation báo lỗi -> agent cần fallback phù hợp và không “bịa”.
   - Nếu observation cho thấy mức nguy hiểm (`dangerous`) -> safety layer phải chặn/ESCALATE.

---

## IV. Future Improvements (5 Points)

- **Scalability**:
  - Tách tool execution thành async worker (queue) để xử lý nhiều request đồng thời.
  - Thêm tool router theo intent để giảm số bước ReAct và giảm latency.

- **Safety**:
  - Bổ sung policy layer độc lập (rule-based + classifier) trước và sau tool execution.
  - Thêm audit log chuẩn JSON cho toàn bộ action chain để truy vết sự cố.

- **Performance**:
  - Cache kết quả các tool call lặp lại theo fingerprint của args.
  - Chuẩn hóa schema dữ liệu thuốc ngay từ source để tránh conversion runtime.
  - Dùng retrieval/embedding cho tập dữ liệu lớn nếu mở rộng nhiều nguồn tri thức.

---

> [!NOTE]
> Đổi tên file này thành `REPORT_[YOUR_NAME].md` trước khi nộp.
