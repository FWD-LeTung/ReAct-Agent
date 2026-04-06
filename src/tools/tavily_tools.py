import re
import io
import pandas as pd
from tavily import TavilyClient

TAVILY_API_KEY = "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"


def _extract_rate(text: str) -> str:
    """
    Trích số lãi suất từ text và chuẩn hóa giống tool cũ.
    Ví dụ:
    '6.2%/năm' -> '6.2'
    """
    text = str(text)

    match = re.search(r"(\d+(?:[\.,]\d+)?)\s*%", text)
    if match:
        return match.group(1).replace(",", ".")
    return "-"


def fetch_interest_rates(bank_name: str = "all", type_rate: str = "all") -> str:
    """
    GIỮ NGUYÊN INPUT/OUTPUT như tool cũ:
    - input: bank_name, type_rate
    - output: CSV string
    """

    client = TavilyClient(api_key=TAVILY_API_KEY)

    # giữ logic query theo input cũ
    if bank_name.lower() == "all":
        query = "bảng lãi suất tiết kiệm ngân hàng Việt Nam mới nhất online tại quầy"
    else:
        query = f"lãi suất tiết kiệm {bank_name} mới nhất"

    if type_rate.lower() == "online":
        query += " online"
    elif type_rate.lower() == "tai_quay":
        query += " tại quầy"

    try:
        result = client.search(
            query=query,
            max_results=5,
            search_depth="advanced"
        )

        rows = []

        for item in result.get("results", []):
            title = item.get("title", "")
            content = item.get("content", "")

            # đoán tên ngân hàng từ title/query
            detected_bank = bank_name if bank_name.lower() != "all" else title[:30]

            rate = _extract_rate(content)

            rows.append({
                "Ngan_hang": detected_bank,
                "Hinh_thuc": type_rate if type_rate != "all" else "Online",
                "1T": rate,
                "3T": rate,
                "6T": rate,
                "12T": rate
            })

        if not rows:
            return "Lỗi: Không tìm thấy dữ liệu."

        df = pd.DataFrame(rows)

        return df.to_csv(index=False)

    except Exception as e:
        return f"Lỗi thực thi Tavily: {str(e)}"
