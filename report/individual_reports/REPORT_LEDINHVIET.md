# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: [Lê Đình Việt]
- **Student ID**: [2A202600469]
- **Date**: [06/04/2026]

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: [e.g., `src/chatbot/chatbot.py`]
- **Code Highlights**: [import os
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
    main()]
- **Documentation**: [Nhiệm vụ của tôi trong nhóm là xây dựng một chatbot đơn giản có khả năng trả lời về thông tin lãi suất và cách tính tiền lãi cho khách hàng. Khi trả lời những câu hỏi của người dùng, tôi tổng hợp lại lỗi sai và cách cải thiện chatbot bằng ReAct Agent cho mọi người làm Giai đoạn 3]

---

## II. Debugging Case Study (10 Points)

### Problem Description
Một failure phức tạp xảy ra khi Agent:

- Tool chính `fetch_interest_rates` bị lỗi (Playwright chưa cài browser)
- Agent fallback sang `tavily_search`
- Nhưng kết quả search **không ổn định / không chính xác**
- Agent tiếp tục reasoning nhiều bước → tăng latency, token cost
- Cuối cùng trả lời **dựa trên dữ liệu không đáng tin (hallucination risk)**

Đây là case **multi-step failure chain**:
Tool 1 fail → Tool 2 noisy → reasoning lệch → output sai tiềm ẩn


---

### Log Source
Trích từ log: :contentReference[oaicite:0]{index=0}

**Step 1 – Tool chính fail:**
Action: fetch_interest_rates(...)
Observation: BrowserType.launch error (Playwright missing)


**Step 2 – Fallback sang search:**

Action: tavily_search(...)
Observation: Không tìm thấy thông tin phù hợp


**Step 3 – Retry search với query khác:**

Action: tavily_search(...)
Observation: trả về dữ liệu cũ (10/2023, 5.5%)


**Step 4 – Agent vẫn kết luận:**

Final Answer: Lãi suất cao nhất là 5.5%


---

### Diagnosis

**1. Failure cascade (chuỗi lỗi liên tiếp)**

- Tool chính fail → mất nguồn dữ liệu chuẩn
- Tool phụ (search) trả dữ liệu:
  - outdated
  - không kiểm chứng
- Agent không phân biệt được độ tin cậy

---

**2. LLM reasoning limitation**

- LLM vẫn tin rằng:
``` id="n3x8yz"
search result = ground truth
Không có cơ chế:
kiểm tra freshness (2023 vs hiện tại)
cross-check nhiều nguồn

**3. Prompt chưa kiểm soát chất lượng dữ liệu**

Thiếu rule:

- If data is outdated → warn user
- If confidence low → do not finalize immediately

**4. Cost & latency issue**

Log cho thấy:

Step tăng từ 2 → 3
Token tăng mạnh:
total_tokens: 955
latency: 8396ms

Agent trở nên expensive nhưng không chính xác hơn

Solution
1. Fix tool (root)
playwright install
2. Add reliability layer (rất quan trọng)

Trong system prompt:

- If tool output is outdated → mention uncertainty
- Prefer multiple sources before final answer
- If confidence is low → ask user instead of guessing
---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. Reasoning

ReAct cho phép multi-step reasoning:

Tool fail → switch tool → retry → finalize

Chatbot không làm được chain này

2. Reliability

Case này cho thấy:

ReAct có thể tệ hơn chatbot khi:

Tool unreliable
Data noisy
Không có validation layer

Chatbot:

Trả lời general nhưng ổn định

Agent:

Trả lời “có vẻ đúng” nhưng thực ra sai (dangerous)

3. Observation

Observation ảnh hưởng mạnh:

Error → đổi tool
No data → retry
Weak data → vẫn finalize

Vấn đề:
Agent không hiểu chất lượng observation


---

## IV. Future Improvements (5 Points)

Scalability
Multi-tool orchestration (planner + executor)
Async execution cho search + scraping
Safety
Add "Critic Agent":
check:
- data freshness
- source reliability
- contradiction
Performance
Cache interest rates (daily update)
Vector DB để tránh search lại

---