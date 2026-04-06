import os
import sys
import time
from collections import deque
from typing import Optional, List, Dict, Any
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.core.openai_provider import OpenAIProvider

# Load environment variables from .env file
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)


class SimpleChatbot:
    """
    A chatbot that uses OpenAI API.
    Specializes in Vietnamese bank interest rates calculation and consultation.
    Maintains conversation history (last 10 messages).
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o"):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables.")

        self.provider = OpenAIProvider(model_name=model_name, api_key=api_key)

        self.history = deque(maxlen=10)

        self.system_prompt = """Bạn là một trợ lý AI hỗ trợ tra cứu lãi suất ngân hàng Việt Nam và tính toán lãi suất.

NHIỆM VỤ CỦA BẠN:
1. Tra cứu và cung cấp thông tin lãi suất hàng của các ngân hàng Việt Nam
2. Tính toán lãi suất dựa trên:
- Khoản tiền gửi/vay (số tiền)
- Thời gian gửi/vay (tháng, năm)
- Lãi suất hàng năm (%)
- Phương thức tính lãi (lãi đơn hoặc lãi kép)

HƯỚNG DẪN:
- Nếu thiếu thông tin → yêu cầu ngay
- Sau khi đủ:
  * Xác nhận input
  * Tính toán
  * Giải thích
  * Hiển thị kết quả

CÔNG THỨC:
- Lãi đơn: Lãi = Số tiền × Lãi suất × Số năm / 100
- Lãi kép: S = P × (1 + r)^n

Luôn thân thiện, chuyên nghiệp."""

    def _format_context(self) -> str:
        if not self.history:
            return ""

        context = "\n\nLịch sử cuộc trò chuyện:"
        for i, (q, a) in enumerate(self.history, 1):
            context += f"\nCâu hỏi {i}: {q}\nTrả lời {i}: {a}"
        return context

    def chat(self, user_input: str) -> Dict[str, Any]:
        start_time = time.time()

        context = self._format_context()
        full_prompt = f"{user_input}{context}"

        response_data = self.provider.generate(
            full_prompt,
            system_prompt=self.system_prompt
        )

        latency = time.time() - start_time

        response_text = response_data.get("content", "")
        usage = response_data.get("usage", {})

        result = {
            "content": response_text,
            "latency": latency,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
        }

        self.history.append((user_input, response_text))

        return result

    def run_interactive(self):
        print("=" * 60)
        print("Nhập câu hỏi (exit để thoát, history để xem lịch sử):\n")

        try:
            while True:
                user_input = input("Bạn: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "exit":
                    print("Tạm biệt!")
                    break

                if user_input.lower() == "history":
                    self._print_history()
                    continue

                print("\nChatbot: ", end="", flush=True)

                try:
                    result = self.chat(user_input)

                    print(result["content"])
                    print("\n---")
                    print(f"⏱️ Latency: {result['latency']:.2f}s")
                    print(f"🔢 Input tokens: {result['prompt_tokens']}")
                    print(f"🔢 Output tokens: {result['completion_tokens']}")
                    print()

                except Exception as e:
                    print(f"Lỗi: {str(e)}\n")

        except KeyboardInterrupt:
            print("\n\nChatbot đã dừng.")

    def _print_history(self):
        if not self.history:
            print("\nKhông có lịch sử.\n")
            return

        print("\n" + "=" * 60)
        print("Lịch sử (10 câu gần nhất):")
        print("=" * 60)

        for i, (q, a) in enumerate(self.history, 1):
            print(f"\n[{i}] Câu hỏi: {q}")
            print(f"    Trả lời: {a[:100]}..." if len(a) > 100 else f"    Trả lời: {a}")

        print("\n" + "=" * 60 + "\n")


def main():
    try:
        chatbot = SimpleChatbot()
        chatbot.run_interactive()
    except ValueError as e:
        print(f"Lỗi khởi tạo: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()