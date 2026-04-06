# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: [E402_07]
- **Team Members**: [
  2A202600474 Mã Khoa Học
  2A202600232 Nguyễn Tuấn Kiệt
  2A202600397 Nguyễn Hữu Nam
  2A202600428 Trần Ngô Hồng Hà
  2A202600244 Nguyễn Việt Trung
  2A202600055 Hà Việt Khánh
  ]
- **Deployment Date**: [2026-04-06]

---

## 1. Executive Summary

Dự án xây dựng hệ thống tư vấn tra cứu thuốc và tương tác thuốc, triển khai dưới hai phiên bản để so sánh trực tiếp: Chatbot Baseline (LLM thuần) và ReAct Agent (LLM + tool calls). Cùng một bộ câu hỏi đầu vào được chạy qua cả hai hệ thống, kết quả cho thấy agent vượt trội rõ rệt ở các tình huống cần tra cứu dữ liệu chính xác và tính toán liều lượng.

- **Success Rate**: Agent đạt [X]/5 test cases chính xác hoàn toàn, Chatbot đạt [Y]/5
- **Key Outcome**: "Agent giải quyết được 100% các câu hỏi liên quan đến tương tác thuốc nguy hiểm nhờ gọi `check_interaction()`, trong khi Chatbot baseline hallucinate tên thuốc và đưa ra liều lượng sai ở 3/5 test cases."

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation

Agent hoạt động theo vòng lặp Thought → Action → Observation, lặp lại cho đến khi đủ thông tin để trả lời hoặc chạm điều kiện dừng.

```

User Input
│
▼
[Reason] LLM suy luận: cần thông tin gì? Tool nào phù hợp?
│
▼
[Action] Gọi tool tương ứng với arguments được trích xuất
│
▼
[Observation] Nhận kết quả từ tool, đưa lại vào context
│
▼
[Sufficient?] Đủ thông tin? → Có: sinh câu trả lời / Không: quay lại Reason
│
▼
[Safety Check] Phát hiện tương tác nguy hiểm? → ESCALATE / Fallback / Trả lời bình thường

```

Giới hạn vòng lặp tối đa: **5 iterations** để tránh vòng lặp vô hạn.

### 2.2 Tool Definitions (Inventory)

| Tool Name           | Input Format                                                        | Use Case                                                                                             |
| :------------------ | :------------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------- |
| `search_drug`       | `{"drug_name": string}`                                             | Tra cứu thông tin thuốc: liều dùng, chỉ định, chống chỉ định từ mock database                        |
| `check_interaction` | `{"drug1": string, "drug2": string}`                                | Kiểm tra tương tác giữa 2 loại thuốc, trả về mức độ nguy hiểm (dangerous / moderate / caution / low) |
| `calculate_dose`    | `{"drug_name": string, "weight_kg": float, "age_years": int/float}` | Tính liều lượng phù hợp theo cân nặng và tuổi bệnh nhân                                              |

### 2.3 LLM Providers Used

- **Primary**: Gemini Flash (Google) — dùng cho Chatbot Baseline qua LangChain
- **Secondary**: GPT-4o Mini (OpenAI) — dùng cho ReAct Agent

---

### 2.4 Tool Design Evolution (v1 → v2)

Team đã thực hiện mô hình **merged versioning**: v1 và v2 được phát triển liên tiếp trong cùng một codebase, v2 được bổ sung trực tiếp vào agent thay vì tách file riêng.

#### v1 — Core Tool Set (Initial Design)

Mục tiêu: agent có thể gọi tool để tra cứu thông tin thay vì hallucinate.

| Tool                | Spec v1                                                                                               |
| :------------------ | :---------------------------------------------------------------------------------------------------- |
| `search_drug`       | Input: `drug_name: string` → tra cứu mock DB, trả về dict thông tin thuốc hoặc `null`                 |
| `check_interaction` | Input: `drug1, drug2: string` → trả về `{"interaction": "dangerous"/"moderate"/"caution"/"low", ...}` |

**Điểm yếu phát hiện trong v1:**

- Không xử lý khi tool trả về `null` hoặc `"unknown"` — agent vẫn có thể hallucinate từ `Final Answer`
- Không có cơ chế cưỡng bắt escalate khi `interaction == "dangerous"` — để LLM tự quyết
- Không có tool tính liều → chatbot phải đoán khi user hỏi liều theo cân nặng

#### v2 — Failure Handling + Expanded Tooling

Mục tiêu: bịt 3 lỗ hổng trên.

| Thay đổi                     | Cách implement                                                                                                         |
| :--------------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| **Thêm `calculate_dose`**    | Input: `drug_name, weight_kg, age_years` → tính liều theo nhóm tuổi (child/adult), loại bỏ hallucination liều          |
| **Grounding check**          | `_has_grounded_data(observations)` — nếu không có observation hợp lệ từ tool, từ chối trả lời thay vì để LLM tự suy    |
| **Tool error guard**         | `_has_tool_errors(observations)` — phát hiện `{"error": ...}` trong observation, trả về thông báo lỗi thay vì tiếp tục |
| **Bắt buộc ESCALATE**        | `_safety_check()` scan observation JSON: nếu `interaction == "dangerous"` → prepend cảnh báo đỏ, không để LLM soften   |
| **Harmful intent detection** | Regex trên `user_input` bắt các pattern nguy hiểm (`tự tử`, `đầu độc`, ...) → hard escalate                            |
| **Max steps guard**          | `max_steps=5` + forced summary prompt nếu vòng lặp hết bước                                                            |

#### So sánh trực tiếp v1 vs v2

| Scenario                         | v1 Output                    | v2 Output                                      |
| :------------------------------- | :--------------------------- | :--------------------------------------------- |
| Tool trả về null                 | LLM có thể bịa               | Fallback: "không có dữ liệu"                   |
| `interaction = "dangerous"`      | LLM softens thành "cẩn thận" | Hard escalate + cảnh báo đỏ                    |
| Hỏi liều Amoxicillin 8kg, 2 tuổi | Đoán theo training data      | `calculate_dose()` → 160–320mg/ngày chia 3 lần |
| Tool call thất bại               | Agent crash hoặc hallucinate | Error guard → yêu cầu nhập lại                 |

---

## 3. Telemetry & Performance Dashboard

_Số liệu đo trong lần chạy test suite 5 test cases cuối buổi._

- **Average Latency (P50)**: [3990 ms] — Agent thường chậm hơn Chatbot do có thêm tool call round-trip
- **Max Latency (P99)**: [5728 ms] — xảy ra ở TC2 (tương tác thuốc) khi agent lặp 2 vòng Reason
- **Average Tokens per Task**: Chatbot ~[1000] tokens / Agent ~[1200] tokens (cao hơn do có Observation context)
- **Total Tool Calls trong Test Suite**: [3] calls trên 5 test cases
- **Escalation Triggered**: [1]/5 cases — đúng với TC2 (Warfarin + Ibuprofen)
- **Fallback Triggered**: [1]/5 cases — đúng với TC4 (thuốc không tồn tại)

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study 1: Chatbot hallucinate liều Paracetamol (TC1)

- **Input**: "Thuốc Paracetamol uống bao nhiêu mg?"
- **Chatbot Output**: Trả lời "500mg mỗi 4 giờ, tối đa 4g/ngày" — đúng với người lớn nhưng không hỏi thêm thông tin bệnh nhân, không phân biệt trẻ em / người suy gan.
- **Agent Output**: Gọi `search_drug("Paracetamol")` → nhận đủ thông tin theo nhóm đối tượng → hỏi lại cân nặng nếu cần → trả lời có phân nhóm rõ ràng.
- **Root Cause (Chatbot)**: System prompt không yêu cầu chatbot hỏi thêm thông tin bệnh nhân trước khi trả lời liều. Dữ liệu trong training có thể outdated với một số thuốc.

### Case Study 2: Agent escalate đúng tương tác Warfarin + Ibuprofen (TC2)

- **Input**: "Tôi đang uống Warfarin, có thể uống Ibuprofen không?"
- **Chatbot Output**: "Bạn nên cẩn thận khi kết hợp hai thuốc này" — mơ hồ, không có cảnh báo rõ ràng.
- **Agent Output**: Gọi `check_interaction("Warfarin", "Ibuprofen")` → nhận `{"interaction": "dangerous", ...}` (Warfarin = "Thuốc chống đông máu", Ibuprofen = "NSAID" → khớp rule `dangerous`) → trigger ESCALATE → in cảnh báo đỏ và khuyến nghị gặp dược sĩ ngay.
- **Root Cause (Chatbot)**: LLM biết tương tác này nhưng không có cơ chế bắt buộc escalate — câu trả lời bị làm mềm đi do safety training của LLM.

> **Lưu ý**: Trong mock DB, Aspirin được phân loại "Thuốc giảm đau" (không phải NSAID), nên cặp Warfarin + Aspirin chỉ trả về mức "low". Cặp kích hoạt ESCALATE là Warfarin + **Ibuprofen** (NSAID).

### Case Study 3: Agent fallback đúng với thuốc không tồn tại (TC4)

- **Input**: "Thuốc XYZ123 trị bệnh gì?"
- **Agent Output**: Gọi `search_drug("XYZ123")` → nhận `{"found": false}` → trả về fallback "Không tìm thấy thông tin thuốc này, vui lòng hỏi dược sĩ hoặc bác sĩ."
- **Root Cause nếu fail**: Nếu agent không gọi tool mà trả lời thẳng, LLM có thể bịa ra thông tin thuốc — đây là rủi ro lớn nhất của chatbot baseline.

---

## 5. Ablation Studies & Experiments

### Experiment 1: System Prompt v1 vs v2 (Chatbot Baseline)

- **Diff**: Prompt v2 thêm instruction "Nếu câu hỏi liên quan đến liều lượng, hãy hỏi thêm: tuổi và cân nặng bệnh nhân trước khi trả lời."
- **Result**: TC3 (liều trẻ em) từ sai sang đúng hướng — chatbot hỏi thêm thông tin thay vì đoán. Tuy nhiên vẫn không chính xác bằng agent vì không có `calculate_dose()`.

### Experiment 2 (Bonus): Chatbot vs Agent — Bảng so sánh đầy đủ

| Test Case | Input tóm tắt                  | Chatbot Result                 | Agent Result                                            | Winner    |
| :-------- | :----------------------------- | :----------------------------- | :------------------------------------------------------ | :-------- |
| TC1       | Liều Paracetamol               | Đúng nhưng thiếu phân nhóm     | Đúng, phân nhóm theo đối tượng                          | **Agent** |
| TC2       | Warfarin + Ibuprofen           | Mơ hồ, không escalate          | Escalate đúng, cảnh báo rõ                              | **Agent** |
| TC3       | Liều Amoxicillin bé 8kg 2 tuổi | Sai liều (dùng liều người lớn) | Đúng qua `calculate_dose()` → 160–320mg/ngày chia 3 lần | **Agent** |
| TC4       | Thuốc XYZ123 không tồn tại     | Bịa thông tin thuốc            | Fallback đúng                                           | **Agent** |
| TC5       | "Tôi bị đau đầu uống gì?"      | Gợi ý ngay không hỏi thêm      | Hỏi thêm triệu chứng trước                              | **Agent** |

---

## 6. Production Readiness Review

- **Security**: Sanitize input trước khi đưa vào tool arguments — tránh injection qua tên thuốc. Validate kiểu dữ liệu `weight_kg` và `age` phải là số dương trước khi gọi `calculate_dose()`.
- **Guardrails**: Giới hạn tối đa 5 vòng lặp ReAct để tránh vòng lặp vô hạn và chi phí token không kiểm soát. Bất kỳ kết quả `dangerous` nào từ `check_interaction()` đều bắt buộc trigger ESCALATE, không để LLM tự quyết định.
- **Disclaimer y tế**: Mọi output đều kèm dòng "Thông tin chỉ mang tính tham khảo, không thay thế tư vấn của bác sĩ hoặc dược sĩ."
- **Scaling**: Thay mock database bằng API dược thư quốc gia thực. Migrate sang LangGraph nếu cần branching phức tạp hơn (ví dụ: agent hỏi đa vòng với bệnh nhân). Thêm logging mỗi tool call để audit sau này.
- **Data freshness**: Mock data hiện tại chứa 22 loại thuốc (12 thuốc phổ biến + 10 thuốc mới như Alyftrek, Datroway, Journavx, Aficamten, ...) — production cần kết nối database cập nhật định kỳ khi có thuốc mới hoặc thay đổi phác đồ.

---

> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in this folder.
