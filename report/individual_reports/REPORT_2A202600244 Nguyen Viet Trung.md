# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Việt Trung
- **Student ID**: 2A202600244
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

### Modules Implemented

- **`app.py`** (project root) — Unified Streamlit entry point: radio selector cho hai chế độ (💬 Chatbot / 🧪 ReAct Agent), session metrics dashboard trên sidebar, per-turn metrics expander.
- **`src/agent/agent.py`** — Tích hợp `tracker.track_request()` sau mỗi lần gọi LLM, thêm `last_run_stats` dict và `_safety_type` flag vào `ReActAgent`.
- **Bug fix** — Sửa `TypeError` trong chatbot mode (`response.content[0]["text"]` → `response.content`).

---

### Code Highlights

**1. `app.py` — Chatbot mode với per-turn metrics từ `usage_metadata`**

Chatbot dùng LangChain + Gemini Flash. Sau mỗi lượt, `response.usage_metadata` trả về token count thực tế, được ghi vào `chatbot_turn_stats` và hiện trong expander:

```python
t0 = time.time()
response = chain.invoke({"history": st.session_state.chatbot_history})
latency_ms = int((time.time() - t0) * 1000)

bot_reply = response.content
usage = response.usage_metadata or {}
turn_s = {
    "latency_ms": latency_ms,
    "input_tokens": usage.get("input_tokens", 0),
    "output_tokens": usage.get("output_tokens", 0),
    "total_tokens": usage.get("total_tokens", 0),
}
st.session_state.chatbot_turn_stats.append(turn_s)

ai_msg = AIMessage(content=bot_reply, additional_kwargs={"_metrics": turn_s})
st.session_state.chatbot_history.append(ai_msg)
```

Metrics được nhúng vào `AIMessage.additional_kwargs["_metrics"]` để khi render lại lịch sử hội thoại vẫn hiển thị đúng số liệu của từng lượt.

**2. `app.py` — Session metrics dashboard (sidebar)**

Sidebar tính toán P50/P99 latency và token aggregates từ `agent_turn_stats` session state:

```python
turn_stats = st.session_state.get("agent_turn_stats", [])
if turn_stats:
    n = len(turn_stats)
    avg_latency = sum(s.get("total_latency_ms", 0) for s in turn_stats) // n
    max_latency = max(s.get("total_latency_ms", 0) for s in turn_stats)
    n_escalate = sum(1 for s in turn_stats if s.get("escalation_triggered"))
    n_fallback  = sum(1 for s in turn_stats if s.get("fallback_triggered"))
    c1.metric("Avg Latency", f"{avg_latency} ms")
    c2.metric("P99 Latency", f"{max_latency} ms")
    c1.metric("Escalations", f"{n_escalate}/{n}")
    c2.metric("Fallbacks",   f"{n_fallback}/{n}")
```

Dùng `.get("agent_turn_stats", [])` thay vì attribute access để tránh `AttributeError` khi sidebar render trước block khởi tạo session state.

**3. `src/agent/agent.py` — Tích hợp `tracker.track_request()`**

`PerformanceTracker.track_request()` ghi event `LLM_METRIC` vào log file (dùng bởi `evaluate_metrics.py`). Trước khi tích hợp, hàm này chưa bao giờ được gọi → log trống. Thêm call sau mỗi `llm.generate()` trong vòng lặp ReAct:

```python
tracker.track_request(
    provider=(result or {}).get("provider", "unknown"),
    model=self.llm.model_name,
    usage=_u,
    latency_ms=(result or {}).get("latency_ms", 0),
)
```

Log kết quả trong `logs/2026-04-06.log`:

```json
{
  "timestamp": "...",
  "event": "LLM_METRIC",
  "data": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "prompt_tokens": 512,
    "completion_tokens": 128,
    "total_tokens": 640,
    "latency_ms": 1823,
    "cost_estimate": 0.0064
  }
}
```

---

## II. Debugging Case Study (10 Points)

### Problem: `TypeError: string indices must be integers` — Chatbot không trả lời được

**Mô tả:** Khi chạy chatbot mode trong `app.py`, mọi tin nhắn đều gây lỗi tại dòng xử lý response.

**Stack trace:**

```
TypeError: string indices must be integers
  File "app.py", line 60 (approx.)
    bot_reply = response.content[0]["text"]
```

**Chẩn đoán:**

Code gốc trong `src/chatbot/chatbot.py` được viết cho **Anthropic API**, nơi `response.content` là một list of blocks:

```python
# Anthropic format:
response.content[0]["text"]  # → "Hello"
```

Nhưng chatbot dùng **LangChain `ChatGoogleGenerativeAI`** — `response` là `AIMessage`, và `response.content` là plain string:

```python
# LangChain format:
response.content  # → "Hello"  (không phải list)
```

Truy cập `response.content[0]` trên string "Hello" trả về `"H"` (ký tự đầu tiên), sau đó `"H"["text"]` ném `TypeError` vì string không thể index bằng key.

**Fix:**

```python
# Before (sai model API):
bot_reply = response.content[0]["text"]

# After (LangChain AIMessage):
bot_reply = response.content
```

**Bài học:** Khi switch provider (Anthropic → Google via LangChain), response format thay đổi hoàn toàn. Không nên assume response object structure mà không đọc docs/type hints của từng provider.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

**1. Reasoning — `Thought` block giúp ích gì so với Chatbot thuần?**

Chatbot thuần (baseline) trả lời tương tác thuốc dựa hoàn toàn vào knowledge training — model có thể biết Warfarin + Ibuprofen là nguy hiểm, nhưng không có cơ chế xác minh bắt buộc. ReAct agent buộc model viết tường minh:

```
Reason: Cần kiểm tra tương tác Warfarin + Ibuprofen
Action: {"tool": "check_interaction", "args": {"drug1": "Warfarin", "drug2": "Ibuprofen"}}
Observation: {"interaction": "dangerous", "message": "NSAID làm tăng nguy cơ chảy máu..."}
```

`Observation` từ tool là external ground truth — model ở bước `Reason` tiếp theo không thể "ignore" hay "soften" khi tool đã trả về `"dangerous"`. `_safety_check()` trong `agent.py` scan observation JSON và hard-code escalate nếu phát hiện `"interaction": "dangerous"`.

**2. Reliability — Khi nào Agent tệ hơn Chatbot?**

Quan sát thực tế khi chạy test cases:

- **Câu hỏi FAQ đơn giản** (`"Paracetamol là thuốc gì?"`): Chatbot trả lời ngay trong 1 round trip ~800ms. Agent mất thêm 1-2 bước Reason/Action không cần thiết, latency tăng lên ~2000ms, và đôi khi parse `Action` sai format (thiếu dấu ngoặc nhọn) dẫn đến `format_fallback`.
- **Vòng lặp tool thất bại**: Nếu `search_drug()` trả về `{"status": "not_found"}`, agent có thể lặp lại `Action: search_drug` với cùng argument ở vòng tiếp theo thay vì chuyển sang `Final Answer`. `_has_grounded_data()` phát hiện pattern này và trigger fallback.

**3. Observation — Feedback từ môi trường ảnh hưởng thế nào?**

`Observation` là feedback loop bắt buộc model phải "thừa nhận" kết quả thực tế. Trong chatbot baseline, model có thể tự "thuyết phục" mình rằng tương tác là nhẹ do safety training. Với ReAct: sau khi nhận `Observation: {"interaction": "dangerous"}`, model không còn đường thoát nào để đưa ra câu trả lời an toàn mà không vi phạm các `Luật nghiêm ngặt` trong system prompt. Đây là lý do `_safety_check()` scan cả list `observations` lẫn `transcript` chứ không chỉ dựa vào `draft_answer` của LLM.

---

## IV. Future Improvements (5 Points)

- **Scalability**: `tracker.track_request()` hiện ghi log trong main thread Streamlit — khi nhiều user đồng thời, I/O log file có thể gây block. Đưa telemetry vào background task với `asyncio` hoặc một message queue (Redis Streams), tách hoàn toàn khỏi request path.

- **Safety**: Triển khai **Supervisor LLM** — một model nhỏ hơn (Gemini Flash) đọc output của agent trước khi hiển thị cho user, kiểm tra xem response có chứa liều lượng tuyệt đối hoặc lời khuyên y tế trực tiếp không. Nếu vi phạm → rewrite hoặc từ chối. Hiện tại `_safety_check()` chỉ check via regex pattern và JSON key, dễ bị bypass nếu LLM diễn đạt nguy hiểm bằng văn xuôi.

- **Observability**: `evaluate_metrics.py` hiện parse log bằng regex line-by-line — giòn và chậm với log lớn. Thay bằng structured log sink (OpenTelemetry + Jaeger hoặc Grafana Loki) để trace toàn bộ ReAct loop — từng `Reason/Action/Observation` — thành một span duy nhất với parent-child hierarchy.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
