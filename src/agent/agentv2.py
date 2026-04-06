import os
import sys
import importlib.util
from pathlib import Path

from dotenv import load_dotenv

from src.agent.agent import ReActAgent


def _stdout_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _load_module_from_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {module_name} from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_tools():
    """
    IMPORTANT: Do NOT import `src.tools.*` as a package, because `src/tools/__init__.py`
    may reference files that don't exist in your current lab state.
    We load modules directly from their file paths instead.
    """
    root = Path(__file__).resolve().parent
    bank_tools = _load_module_from_path("bank_tools", root / "src" / "tools" / "bank_tools.py")
    calc_tools = _load_module_from_path("calculate", root / "src" / "tools" / "calculate.py")
    tavily_tool = _load_module_from_path("tavily_search", root / "src" / "tools" / "tavily_search.py")

    # Tool 1: crawl bank interest table (CSV string)
    def tool_fetch_interest_rates(bank_name: str = "all", type_rate: str = "all") -> str:
        try:
            return bank_tools.fetch_interest_rates(bank_name=bank_name, type_rate=type_rate)
        except Exception as e:
            return f"Tool execution failed: {type(e).__name__}: {e}"

    # Tool 2: compute interest from principal/rate/duration
    def tool_calculate_interest(
        amount: float,
        rate: float,
        duration: int,
        interest_type: str = "simple",
        withdraw_time: int | None = None,
        withdraw_amount: float | None = None,
    ):
        try:
            return calc_tools.calculate(
                amount=amount,
                rate=rate,
                duration=duration,
                interest_type=interest_type,
                withdraw_time=withdraw_time,
                withdraw_amount=withdraw_amount,
            )
        except Exception as e:
            return f"Tool execution failed: {type(e).__name__}: {e}"

    # Tool 3: Tavily search
    def tool_tavily_search(query: str, max_results: int = 5) -> str:
        try:
            return tavily_tool.search_tavily(query=query, max_results=max_results)
        except Exception as e:
            return f"Tool execution failed: {type(e).__name__}: {e}"

    return [
        {
            "name": "fetch_interest_rates",
            "description": (
                "Cào bảng lãi suất tiết kiệm từ webgia.com và trả về CSV dạng chuỗi. "
                "Input JSON: {bank_name: 'all' hoặc tên ngân hàng, type_rate: 'all'|'tai_quay'|'online'}."
            ),
            "func": tool_fetch_interest_rates,
        },
        {
            "name": "calculate",
            "description": (
                "Tính lãi suất/tiền lãi. Input JSON: "
                "{amount: VND, rate: %/năm, duration: tháng, interest_type: 'simple'|'compound'(optional), "
                "withdraw_time(optional), withdraw_amount(optional)}. Output: JSON dict."
            ),
            "func": tool_calculate_interest,
        },
        {
            "name": "tavily_search",
            "description": (
                "Tìm kiếm thông tin trên internet. Sử dụng khi cần tra cứu tin tức, sự kiện hoặc thông tin ngoài lượng kiến thức nội bộ (Version 2). "
                "Input JSON: {query: 'nội dung cần tìm', max_results: số lượng kết quả (tùy chọn, mặc định 5)}."
            ),
            "func": tool_tavily_search,
        },
    ]


def main() -> int:
    _stdout_utf8()
    load_dotenv(override=True)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or "your_openai_api_key" in api_key.lower():
        print("ERROR: OPENAI_API_KEY is missing/placeholder in .env")
        return 1

    # This runner uses OpenAI. If the user previously set DEFAULT_MODEL to a Gemini model,
    # force a sane OpenAI default to avoid 404 "model_not_found".
    model = (os.getenv("DEFAULT_MODEL") or "gpt-4o").strip()
    if model.lower().startswith("gemini"):
        print(f"WARNING: DEFAULT_MODEL='{model}' looks like a Gemini model. Using 'gpt-4o' for OpenAI.")
        model = "gpt-4o"

    # Lazy import so `pytest` can run without openai installed.
    from src.core.openai_provider import OpenAIProvider

    llm = OpenAIProvider(model_name=model, api_key=api_key)
    agent = ReActAgent(llm=llm, tools=build_tools(), max_steps=5)

    print(f"Provider: openai | Model: {llm.model_name}")
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

