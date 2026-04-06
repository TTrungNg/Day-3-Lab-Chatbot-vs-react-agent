import argparse
import os

from dotenv import load_dotenv

from src.agent.agent import ReActAgent, default_tools


def build_provider(args):
    provider = args.provider.lower()
    if provider == "openai":
        from src.core.openai_provider import OpenAIProvider

        api_key = args.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY. Set env var or pass --api-key.")
        return OpenAIProvider(model_name=args.model, api_key=api_key)

    if provider == "gemini":
        from src.core.gemini_provider import GeminiProvider

        api_key = args.api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY. Set env var or pass --api-key.")
        return GeminiProvider(model_name=args.model, api_key=api_key)

    if provider == "local":
        from src.core.local_provider import LocalProvider

        model_path = args.model_path or os.getenv("LOCAL_MODEL_PATH")
        if not model_path:
            raise ValueError("Missing local model path. Set LOCAL_MODEL_PATH or pass --model-path.")
        return LocalProvider(model_path=model_path, n_ctx=args.n_ctx, n_threads=args.n_threads)

    raise ValueError(f"Unsupported provider: {args.provider}")


def chat_loop(agent: ReActAgent):
    print("ReAct Agent is running. Type 'exit' or 'quit' to stop.")
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Bye.")
            break
        if not user_input:
            continue

        try:
            answer = agent.run(user_input)
            print(f"Agent: {answer}")
        except Exception as e:
            print(f"Agent error: {e}")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run ReAct tool-using chatbot in CLI.")
    parser.add_argument("--provider", choices=["openai", "gemini", "local"], default="openai")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--max-steps", type=int, default=5)
    parser.add_argument("--model-path", default=None, help="Path to local GGUF model (for --provider local)")
    parser.add_argument("--n-ctx", type=int, default=4096)
    parser.add_argument("--n-threads", type=int, default=None)
    args = parser.parse_args()

    llm = build_provider(args)
    agent = ReActAgent(llm=llm, tools=default_tools(), max_steps=args.max_steps)
    chat_loop(agent)


if __name__ == "__main__":
    main()

