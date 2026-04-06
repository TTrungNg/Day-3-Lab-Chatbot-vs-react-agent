import ast
import json
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.tools.tools import calculate_dose, check_interaction, search_drug


class ReActAgent:
    """
    ReAct-style agent:
    User Input → Reason → Action(tool) → Observation → loop → Final Answer → Safety Check
    """

    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools or []
        self.max_steps = max_steps
        self.history: List[str] = []

    def get_system_prompt(self) -> str:
        tool_lines: List[str] = []
        for t in self.tools:
            name = t.get("name", "")
            desc = t.get("description", "")
            schema = t.get("args_schema")
            if schema:
                try:
                    schema_text = json.dumps(schema, ensure_ascii=False)
                except Exception:
                    schema_text = str(schema)
                tool_lines.append(f"- {name}: {desc}\n  args_schema: {schema_text}")
            else:
                tool_lines.append(f"- {name}: {desc}")

        tool_descriptions = "\n".join(tool_lines) if tool_lines else "(no tools registered)"

        return (
            "Bạn là một ReAct agent. Bạn có thể gọi các tool để lấy thông tin.\n\n"
            "### Tools\n"
            f"{tool_descriptions}\n\n"
            "### Quy trình bắt buộc\n"
            "User Input → Reason → Action → Observation → (lặp nếu chưa đủ) → Final Answer → Safety Check.\n\n"
            "### Format bắt buộc (mỗi lượt)\n"
            "Reason: <ngắn gọn, nêu cần gì và chọn tool nào>\n"
            "Action: {\"tool\": \"<tool_name>\", \"args\": { ... }}\n"
            "Observation: <để trống - hệ thống sẽ điền sau khi chạy tool>\n\n"
            "Khi đã đủ thông tin thì trả về:\n"
            "Final Answer: <câu trả lời cho user>\n\n"
            "### Luật nghiêm ngặt\n"
            "- Chỉ gọi tool nằm trong danh sách Tools.\n"
            "- Args phải là JSON hợp lệ.\n"
            "- Không bịa Observation.\n"
            "- CHỈ trả lời trong phạm vi dữ liệu tool trả về. Nếu không có dữ liệu phù hợp, phải từ chối ngắn gọn.\n"
            "- HÃY ĐỂ Ý LỊCH SỬ HỘI THOẠI: Nếu câu hỏi hiện tại thiếu thông tin (vd: 'liều lượng' mà không nói tên thuốc), hãy dựa vào các tin nhắn trước đó trong 'User Input' để tìm dữ liệu.\n"
            "- Nếu phát hiện rủi ro an toàn (tương tác thuốc 'dangerous' hoặc user yêu cầu hướng dẫn nguy hiểm), "
            "hãy ưu tiên ESCALATE: cảnh báo + khuyến nghị gặp bác sĩ/dược sĩ.\n"
        )

    def run(self, user_input: str) -> str:
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})

        transcript = f"User Input: {user_input}\n"
        steps = 0
        last_observation: Optional[str] = None
        observations: List[str] = []

        while steps < self.max_steps:
            if last_observation is not None:
                transcript += f"Observation: {last_observation}\n"
                last_observation = None

            result = self.llm.generate(transcript, system_prompt=self.get_system_prompt())
            content = (result or {}).get("content", "") or ""
            self.history.append(content)

            final = self._extract_final_answer(content)
            if final is not None:
                safe = self._safety_check(
                    user_input=user_input,
                    draft_answer=final,
                    transcript=transcript,
                    observations=observations,
                )
                logger.log_event("AGENT_END", {"steps": steps + 1, "stop_reason": "final"})
                return safe

            action = self._parse_action(content)
            if action is None:
                safe = self._safety_check(
                    user_input=user_input,
                    draft_answer=content.strip(),
                    transcript=transcript,
                    observations=observations,
                )
                logger.log_event("AGENT_END", {"steps": steps + 1, "stop_reason": "format_fallback"})
                return safe

            tool_name, tool_args = action
            logger.info(f"[TOOL_CALL] name={tool_name} args={tool_args}")
            observation = self._execute_tool(tool_name, tool_args)
            safe_observation = observation.encode("unicode_escape").decode("ascii")
            logger.info(f"[TOOL_OBSERVATION] name={tool_name} observation={safe_observation[:300]}")
            observations.append(observation)

            transcript += f"{content.strip()}\n"
            last_observation = observation
            steps += 1

        logger.log_event("AGENT_END", {"steps": steps, "stop_reason": "max_steps"})
        result = self.llm.generate(
            transcript + "Reason: Đã đủ bước tool. Hãy tóm tắt với thông tin hiện có.\nFinal Answer:",
            system_prompt=self.get_system_prompt(),
        )
        content = (result or {}).get("content", "") or ""
        final = self._extract_final_answer(content) or content.strip()
        return self._safety_check(
            user_input=user_input,
            draft_answer=final,
            transcript=transcript,
            observations=observations,
        )

    def _parse_action(self, llm_text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        # Action: {"tool":"name","args":{...}}
        m = re.search(r"(?im)^\s*Action:\s*(\{.*\})\s*$", llm_text.strip())
        if m:
            raw = m.group(1)
            obj: Any = None
            try:
                obj = json.loads(raw)
            except Exception:
                try:
                    obj = ast.literal_eval(raw)
                except Exception:
                    obj = None
            if isinstance(obj, dict):
                tool = obj.get("tool")
                args = obj.get("args", {})
                if isinstance(tool, str) and isinstance(args, dict):
                    return tool, args

        # Action: tool_name({...})
        m = re.search(r"(?im)^\s*Action:\s*([a-zA-Z_]\w*)\s*\((.*)\)\s*$", llm_text.strip())
        if m:
            tool = m.group(1)
            arg_text = m.group(2).strip()
            if not arg_text:
                return tool, {}
            parsed: Any = None
            for parser in (json.loads, ast.literal_eval):
                try:
                    parsed = parser(arg_text)
                    break
                except Exception:
                    continue
            if isinstance(parsed, dict):
                return tool, parsed
            if isinstance(parsed, (str, int, float)):
                return tool, {"input": parsed}
            return tool, {"input": arg_text}

        return None

    def _extract_final_answer(self, llm_text: str) -> Optional[str]:
        m = re.search(r"(?is)Final Answer:\s*(.+?)\s*$", llm_text.strip())
        if m:
            return m.group(1).strip()
        return None

    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        tool = next((t for t in self.tools if t.get("name") == tool_name), None)
        if tool is None:
            logger.info(f"[TOOL_ERROR] name={tool_name} reason=not_found")
            return json.dumps({"error": f"Tool {tool_name} not found."}, ensure_ascii=False)

        func: Optional[Callable[..., Any]] = tool.get("func") or self._builtin_tool_dispatch(tool_name)
        if func is None:
            logger.info(f"[TOOL_ERROR] name={tool_name} reason=no_callable")
            return json.dumps({"error": f"Tool {tool_name} has no callable bound."}, ensure_ascii=False)

        try:
            if isinstance(args, dict) and "input" in args and len(args) == 1:
                result = func(args["input"])
            else:
                result = func(**(args or {}))
        except TypeError:
            try:
                result = func(args)
            except Exception as e:
                logger.info(f"[TOOL_ERROR] name={tool_name} reason={e}")
                return json.dumps({"error": f"Tool call failed: {e}"}, ensure_ascii=False)
        except Exception as e:
            logger.info(f"[TOOL_ERROR] name={tool_name} reason={e}")
            return json.dumps({"error": f"Tool call failed: {e}"}, ensure_ascii=False)

        try:
            return json.dumps(result, ensure_ascii=False)
        except Exception:
            return str(result)

    def _builtin_tool_dispatch(self, tool_name: str) -> Optional[Callable[..., Any]]:
        mapping: Dict[str, Callable[..., Any]] = {
            "search_drug": search_drug,
            "check_interaction": check_interaction,
            "calculate_dose": calculate_dose,
        }
        return mapping.get(tool_name)

    def _safety_check(
        self,
        user_input: str,
        draft_answer: str,
        transcript: str,
        observations: List[str],
    ) -> str:
        if self._has_tool_errors(observations):
            return (
                "Mình đang gặp lỗi khi truy xuất dữ liệu thuốc cho câu hỏi này. "
                "Bạn thử nhập lại tên thuốc/định dạng câu hỏi, hoặc thử lại sau."
            )

        if not self._has_grounded_data(observations):
            # Cho phép Agent đặt câu hỏi hoặc yêu cầu thêm thông tin để phục vụ việc gọi Tool
            # Bao gồm cả trường hợp Agent hỏi lại tên thuốc nếu lịch sử cũng không có.
            clarifying_keywords = ["bao nhiêu", "như thế nào", "vui lòng", "bạn có thể", "ý bạn là", "thuốc nào", "tên thuốc", "cho mình biết"]
            is_clarifying_question = "?" in draft_answer or any(word in draft_answer.lower() for word in clarifying_keywords)
            if is_clarifying_question:
                return draft_answer.strip()

            return (
                "Xin lỗi, mình chỉ có thể trả lời trong phạm vi dữ liệu thuốc hiện có của hệ thống "
                "(tra cứu thuốc, tương tác thuốc, tính liều)."
            )

        dangerous = False
        for payload in observations:
            try:
                if "\"interaction\"" in payload and "dangerous" in payload:
                    dangerous = True
                    break
                obj = json.loads(payload)
                if isinstance(obj, dict) and obj.get("interaction") == "dangerous":
                    dangerous = True
                    break
            except Exception:
                continue

        try:
            for line in transcript.splitlines():
                if line.strip().startswith("Observation:"):
                    payload = line.split("Observation:", 1)[1].strip()
                    if "\"interaction\"" in payload and "dangerous" in payload:
                        dangerous = True
                        break
                    obj = json.loads(payload)
                    if isinstance(obj, dict) and obj.get("interaction") == "dangerous":
                        dangerous = True
                        break
        except Exception:
            pass

        harmful_patterns = [
            r"\btự\s*tử\b",
            r"\bđầu\s*độc\b",
            r"\bchế\s*tạo\s*thuốc\b",
            r"\bmua\s*thuốc\s*độc\b",
        ]
        harmful = any(re.search(p, user_input, flags=re.IGNORECASE) for p in harmful_patterns)

        if harmful or dangerous:
            logger.log_event(
                "AGENT_SAFETY_ESCALATE",
                {"dangerous_interaction": dangerous, "harmful_request": harmful},
            )
            prefix = (
                "Cảnh báo an toàn: Mình không thể hỗ trợ hướng dẫn nguy hiểm. "
                "Nếu có nguy cơ nghiêm trọng, hãy liên hệ bác sĩ/dược sĩ hoặc cơ sở y tế ngay.\n\n"
            )
            return prefix + draft_answer.strip()

        return draft_answer.strip()

    def _has_grounded_data(self, observations: List[str]) -> bool:
        """
        True when there is at least one meaningful tool observation from dataset.
        """
        if not observations:
            return False

        for payload in observations:
            text = (payload or "").strip()
            if not text or text in {"null", "None"}:
                continue
            # tool/runtime errors are not considered grounded data
            if "\"error\"" in text or "Tool " in text and "not found" in text:
                continue
            try:
                obj = json.loads(text)
                if obj is None:
                    continue
                if isinstance(obj, dict):
                    # Nếu tool trả về lỗi thực sự (thất bại hệ thống) thì không coi là grounded data
                    if "error" in obj:
                        continue
                    # Cho phép các thông tin gợi ý hoặc thông báo thiếu dữ liệu từ tool
                    if "status" in obj or "message" in obj:
                        return True
                    if obj.get("interaction") == "unknown":
                        continue
                    return True
                if isinstance(obj, list) and len(obj) > 0:
                    return True
            except Exception:
                # Non-JSON but non-empty payload is still considered observation.
                return True
        return False

    def _has_tool_errors(self, observations: List[str]) -> bool:
        for payload in observations:
            text = (payload or "").strip()
            if not text:
                continue
            if "\"error\"" in text:
                return True
            try:
                obj = json.loads(text)
                if isinstance(obj, dict) and "error" in obj:
                    return True
            except Exception:
                continue
        return False


def default_tools() -> List[Dict[str, Any]]:
    return [
        {
            "name": "search_drug",
            "description": "Tra cứu thông tin thuốc theo tên.",
            "args_schema": {"drug_name": "string"},
            "func": search_drug,
        },
        {
            "name": "check_interaction",
            "description": "Kiểm tra tương tác giữa 2 thuốc (mock).",
            "args_schema": {"drug1": "string", "drug2": "string"},
            "func": check_interaction,
        },
        {
            "name": "calculate_dose",
            "description": "Tính liều gợi ý theo cân nặng (kg) và tuổi (năm). KHÔNG ĐƯỢC TỰ ĐOÁN cân nặng và tuổi. Nếu user chưa cung cấp thì phải truyền vào 0.",
            "args_schema": {"drug_name": "string", "weight_kg": "number", "age_years": "number"},
            "func": calculate_dose,
        },
    ]
