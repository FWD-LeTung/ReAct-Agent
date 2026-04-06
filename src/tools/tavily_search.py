import os
import requests

def search_tavily(query: str, max_results: int = 5) -> str:
    """
    Tìm kiếm thông tin trên web sử dụng Tavily Search API.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Lỗi: Không tìm thấy TAVILY_API_KEY trong biến môi trường. Vui lòng cấu hình trong file .env."

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": max_results,
        "include_answer": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        if not results:
            return "Không tìm thấy kết quả nào."
            
        formatted_results = []
        for res in results:
            title = res.get("title", "No Title")
            url_link = res.get("url", "No URL")
            content = res.get("content", "No Content")
            formatted_results.append(f"Title: {title}\nURL: {url_link}\nContent: {content}\n")
            
        return "\n---\n".join(formatted_results)
    except Exception as e:
        return f"Lỗi gọi API Tavily: {str(e)}"
