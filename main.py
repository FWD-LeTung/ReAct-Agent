# main.py
import os
from src.core.openai_provider import OpenAIProvider
from src.tools.bank_tools import fetch_interest_rates
from src.tools.calculate import calculate_savings_interest
from src.agent.agent import ReActAgent  

def main():
    
    llm = OpenAIProvider(base_url="https://models.inference.ai.azure.com/",model_name="gpt-4o-mini")

    # Cấu hình danh sách Tools cho Agent

    tools = [
        {
            "name": "fetch_interest_rates",
            "description": "Lấy lãi suất ngân hàng. Tham số: bank_name (str), type_rate ('tai_quay' hoặc 'online').",
            "function": fetch_interest_rates 
        },
        {
            "name": "calculate_savings_interest",
            "description": "Tính tiền lãi. Tham số: principal (float), rate_percent (float), months (int).",
            "function": calculate_savings_interest
        }
    ]

    # Khởi tạo Agent
    agent = ReActAgent(llm=llm, tools=tools, max_steps=10)

    print("=== CHATBOT NGÂN HÀNG - HỎI ĐÁP THÔNG MINH ===")
    print("💡 Tôi có thể giúp bạn tra cứu lãi suất và tính toán tiết kiệm ngân hàng.")
    print("💡 Gõ 'exit', 'quit' hoặc 'thoát' để kết thúc.\n")
    
    # Vòng lặp chatbot
    while True:
        try:
            # Nhận câu hỏi từ người dùng
            user_query = input("👤 Bạn: ").strip()
            
            # Kiểm tra lệnh thoát
            if user_query.lower() in ['exit', 'quit', 'thoát', 'bye']:
                print("\n👋 Cảm ơn bạn đã sử dụng chatbot. Hẹn gặp lại!")
                break
            
            # Bỏ qua nếu câu hỏi rỗng
            if not user_query:
                continue
            
            # Agent xử lý câu hỏi
            print("\n🤖 Agent đang suy nghĩ...\n")
            final_result = agent.run(user_query)
            
            # Hiển thị kết quả
            print("\n" + "="*60)
            print("🤖 Trả lời:")
            print(final_result)
            print("="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Đã dừng chatbot. Hẹn gặp lại!")
            break
        except Exception as e:
            print(f"\n❌ Lỗi: {str(e)}\n")
            continue

if __name__ == "__main__":
    main()
    #dfdff
