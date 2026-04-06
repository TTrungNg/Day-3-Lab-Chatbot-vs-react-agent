import unittest

from src.agent.agent import ReActAgent, default_tools
from src.core.llm_provider import LLMProvider


class FakeLLM(LLMProvider):
    def __init__(self, scripted):
        super().__init__(model_name="fake")
        self.scripted = list(scripted)
        self.calls = 0

    def generate(self, prompt: str, system_prompt=None):
        if self.calls >= len(self.scripted):
            return {"content": "Final Answer: Xin lỗi, mình không có thêm gì.", "usage": {}, "latency_ms": 0}
        out = self.scripted[self.calls]
        self.calls += 1
        return {"content": out, "usage": {}, "latency_ms": 0}

    def stream(self, prompt: str, system_prompt=None):
        yield self.generate(prompt, system_prompt)["content"]


class TestReActAgent(unittest.TestCase):
    def test_agent_calls_tool_then_answers(self):
        llm = FakeLLM(
            [
                'Reason: cần tra cứu thông tin thuốc.\nAction: {"tool":"search_drug","args":{"drug_name":"Ibuprofen"}}\nObservation:',
                "Final Answer: Ibuprofen là một thuốc NSAID (theo dữ liệu mô phỏng).",
            ]
        )
        agent = ReActAgent(llm=llm, tools=default_tools(), max_steps=3)
        out = agent.run("Ibuprofen là thuốc gì?")
        self.assertIn("Ibuprofen", out)
        self.assertEqual(llm.calls, 2)

    def test_agent_escalates_on_dangerous_interaction(self):
        llm = FakeLLM(
            [
                'Reason: cần kiểm tra tương tác.\nAction: {"tool":"check_interaction","args":{"drug1":"Warfarin","drug2":"Ibuprofen"}}\nObservation:',
                "Final Answer: Hai thuốc này có tương tác nguy hiểm (theo dữ liệu mô phỏng).",
            ]
        )
        agent = ReActAgent(llm=llm, tools=default_tools(), max_steps=3)
        out = agent.run("Warfarin và Ibuprofen có tương tác không?")
        self.assertIn("Cảnh báo an toàn", out)

    def test_agent_refuses_out_of_scope_question(self):
        llm = FakeLLM(
            [
                "Final Answer: Paris là thủ đô của Pháp.",
            ]
        )
        agent = ReActAgent(llm=llm, tools=default_tools(), max_steps=2)
        out = agent.run("Thủ đô của Pháp là gì?")
        self.assertIn("chỉ có thể trả lời trong phạm vi dữ liệu thuốc", out)


if __name__ == "__main__":
    unittest.main()

