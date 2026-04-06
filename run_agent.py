import os
import sys

from dotenv import load_dotenv

from src.agent.agent import ReActAgent
from src.tools import get_tools


def _stdout_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def build_provider():
    provider = (os.getenv("DEFAULT_PROVIDER") or "openai").strip().lower()
    model = (os.getenv("DEFAULT_MODEL") or "").strip()

    if provider == "openai":
        from src.core.openai_provider import OpenAIProvider

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or "your_openai_api_key" in api_key.lower():
            raise ValueError(
                "OPENAI_API_KEY is missing/placeholder. Set it in .env (or switch DEFAULT_PROVIDER to google/local)."
            )
        return OpenAIProvider(model_name=model or "gpt-4o", api_key=api_key)

    if provider in ("google", "gemini"):
        from src.core.gemini_provider import GeminiProvider

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or "your_gemini_api_key" in api_key.lower():
            raise ValueError(
                "GEMINI_API_KEY is missing/placeholder. Set it in .env (or switch DEFAULT_PROVIDER to openai/local)."
            )
        return GeminiProvider(model_name=model or "gemini-1.5-flash", api_key=api_key)

    if provider == "local":
        # Optional dependency: llama-cpp-python can be hard to build on Windows.
        from src.core.local_provider import LocalProvider

        model_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
        return LocalProvider(model_path=model_path)

    raise ValueError(f"Unknown DEFAULT_PROVIDER: {provider}")


def main() -> int:
    _stdout_utf8()
    load_dotenv(override=True)

    llm = build_provider()
    agent = ReActAgent(llm=llm, tools=get_tools(), max_steps=5)

    print(f"Provider: {os.getenv('DEFAULT_PROVIDER')} | Model: {llm.model_name}")
    print("Type your question. Ctrl+C to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            return 0

        if not user_input:
            continue

        answer = agent.run(user_input)
        print(f"\nAssistant:\n{answer}\n")


if __name__ == "__main__":
    raise SystemExit(main())

