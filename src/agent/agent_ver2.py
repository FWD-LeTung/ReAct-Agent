import streamlit as st
import openai
from tavily import TavilyClient

# --- 1. CẤU HÌNH ---
TAVILY_API_KEY = "" # Lấy tại tavily.com
OPENAI_API_KEY = ""
tavily = TavilyClient(api_key=TAVILY_API_KEY)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# --- 2. HÀM DỰ BÁO CHUYÊN SÂU ---
def get_ai_prediction(user_input, search_data, history):
    # Prompt mới: Ép Agent phải đưa ra nhận định số liệu
    system_instruction = f"""
    Bạn là một Chuyên gia Phân tích Chiến lược Tài chính cấp cao. 
    DỮ LIỆU THỊ TRƯỜNG MỚI NHẤT: {search_data}
    
    QUY TẮC DỰ BÁO BẮT BUỘC:
    1. KHÔNG trả lời chung chung kiểu 'cần theo dõi thêm' hay 'tùy thuộc vào thị trường'.
    2. PHẢI chọn một xu hướng chủ đạo: TĂNG, GIẢM hoặc ĐI NGANG.
    3. PHẢI đưa ra con số dự báo cụ thể (Ví dụ: "Lãi suất VCB kỳ hạn 12 tháng dự kiến đạt mức 6.2% - 6.5% trong quý tới").
    4. CĂN CỨ LUẬN ĐIỂM: 
       - Nếu Tỷ giá USD/VND > 25.000 -> Dự báo TĂNG lãi suất để giữ nội tệ.
       - Nếu Lạm phát (CPI) > 4% -> Dự báo TĂNG lãi suất để thắt chặt tiền tệ.
       - Nếu các ngân hàng TMCP (Techcombank, VPBank) đã tăng -> Dự báo Big4 (VCB, BIDV) sẽ tăng theo sau 1 tháng.
    5. Phong cách: Quyết đoán, chuyên nghiệp, sử dụng ngôn ngữ của nhà phân tích (VD: 'Dựa trên áp lực tỷ giá...', 'Số liệu cho thấy xu hướng...').
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": user_input}],
        temperature=0.3 # Giảm xuống để con số nhất quán hơn
    )
    return response.choices[0].message.content

# --- 3. GIAO DIỆN STREAMLIT ---
st.set_page_config(page_title="AI Financial Predictor", page_icon="📈")
st.title("📈 AI Predictor: Dự báo Lãi suất Chuyên sâu")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. XỬ LÝ DỰ BÁO ---
if prompt := st.chat_input("Hỏi dự báo ngân hàng cụ thể..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("📊 Đang phân tích biến số vĩ mô và dữ liệu thực tế...", expanded=True):
            # Tìm kiếm cả lãi suất hiện tại VÀ tin tức vĩ mô (tỷ giá, lạm phát)
            search_query = f"lãi suất {prompt} mới nhất tháng 4 2026 tỷ giá USD VND lạm phát Việt Nam"
            search_context = str(tavily.search(query=search_query, max_results=5, search_depth="advanced"))
            st.write("✅ Đã cập nhật dữ liệu tỷ giá và lãi suất liên ngân hàng.")
            
            prediction = get_ai_prediction(prompt, search_context, st.session_state.messages[:-1])
            st.write("✅ Hoàn tất mô hình dự báo.")

        st.markdown(prediction)
        st.session_state.messages.append({"role": "assistant", "content": prediction})

        # Gợi ý hành động sau dự báo
        if "tăng" in prediction.lower():
            st.info("💡 Lời khuyên: Nếu bạn đang định gửi tiền, có thể chờ thêm 1-2 tuần để hưởng mức lãi mới cao hơn.")
        elif "giảm" in prediction.lower():
            st.warning("💡 Lời khuyên: Hãy chốt gói tiết kiệm ngay hôm nay trước khi lãi suất hạ nhiệt.")