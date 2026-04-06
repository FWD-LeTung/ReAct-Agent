# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Ho Bao Thu
- **Student ID**: 2A202600352
- **Date**: 6/4/2026

---
## I. Technical Contribution (15 Points)

Trong bài lab số 3, mình đã phát triển hai hướng tool chính để phục vụ ReAct Agent:

- **bank_tools**: Lấy dữ liệu lãi suất có cấu trúc từ web scraping (webgia.com)
- **tavily_tools**: Truy xuất dữ liệu realtime thông qua search API (Tavily)

---

### Modules Implemented

- `src/tools/tavily_tool.py`  
---

### Code Highlights

- `tavily_tool.py`: phần query + xử lý kết quả Tavily API (search → extract rate → CSV)

### Documentation

- Khi người dùng yêu cầu thông tin lãi suất:
  - LLM phân tích intent và quyết định gọi tool phù hợp:
    - **bank_tools** → khi cần dữ liệu **structured, chính xác theo kỳ hạn**
    - **tavily_tools** → khi cần dữ liệu **realtime hoặc fallback**

- Input truyền vào tool:
  - `bank_name`: tên ngân hàng hoặc `"all"`
  - `type_rate`: `"online"` / `"tai_quay"` / `"all"`

- Output:
  - Cả hai tool đều trả về **CSV string thống nhất format**
  - Giúp Agent dễ dàng:
    - So sánh lãi suất
    - Tính toán
    - Hoặc hiển thị trực tiếp cho user


## II. Debugging Case Study (10 Points)

### Bug 1: Website Anti-bot Blocking

- **Problem Description**:  
Website chặn request khiến việc thu thập dữ liệu không ổn định (bị block, trả về HTML khác hoặc yêu cầu xác thực).

- **Log Source**:  
Không thu được dữ liệu hợp lệ, HTML trả về không chứa bảng lãi suất như mong đợi.

- **Diagnosis**:  
Nguyên nhân đến từ cơ chế **anti-bot protection** của website, không phải do LLM.  
Các request gửi đi thiếu thông tin cần thiết (User-Agent, cookies) hoặc tần suất request quá cao → bị nhận diện là bot.

- **Solution**:  
Sử dụng trình duyệt giả lập (Playwright) để mô phỏng hành vi người dùng thật:

```python
browser = p.chromium.launch(headless=True)
page = browser.new_page(user_agent="Mozilla/5.0...")
## III. Personal Insights: Chatbot vs ReAct (10 Points)

### 1. Reasoning
`Thought` giúp Agent lập kế hoạch trước khi hành động (xác định cần data → gọi tool → truyền tham số).  
So với Chatbot (trả lời trực tiếp, dễ hallucination), ReAct cho kết quả **chính xác hơn với dữ liệu realtime**.

### 2. Reliability
Agent kém hơn Chatbot khi:
- Tool fail (web đổi HTML, anti-bot) → không có data  
- Dễ bị loop nếu model gọi tool sai (ví dụ không dùng `all`)  
→ tăng latency và cost

### 3. Observation
`Observation` là feedback giúp Agent **tự sửa lỗi** (sai input → gọi lại tool → điều chỉnh câu trả lời).

---

## IV. Future Improvements (5 Points)

- **Scalability**: async + caching (Redis)  
- **Safety**: validate input (Pydantic), thêm guardrail  
- **Performance**: tool retrieval + hybrid (`bank_tools` + `tavily_tools`)  


  # Repo nhóm
  ## Link: [!https://github.com/FWD-LeTung/ReAct-Agent.git]
