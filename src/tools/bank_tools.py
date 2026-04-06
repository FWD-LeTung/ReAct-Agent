import pandas as pd
import requests
import io
import re

def extract_number(text):
    """
    Hàm phụ trợ cực mạnh để đối phó với chữ rác của WebGia.
    Lọc bỏ mọi chữ, tìm đúng con số có dấu phẩy.
    """
    text_str = str(text).strip().lower()
    
    # 1. Nếu ô là trống hoặc chứa các ký tự rỗng/vô nghĩa
    if pd.isna(text) or text_str in ['-', '', 'nan']:
        return "-"
        
    # 2. Xóa các chữ chống bot của webgia (nếu họ nhét vào chung với số)
    text_str = text_str.replace("web giá", "").replace("webgiá.com", "").replace("webgia.com", "")
    text_str = text_str.replace("xem tại", "").strip()
    
    if text_str == "":
        return "-" # Nếu xóa chữ xong không còn gì, trả về trống

    # 3. Trích xuất con số dạng thập phân kiểu Việt Nam (vd: 7,05 hoặc 7.05)
    match = re.search(r"(\d+[\.,]\d+|\d+)", text_str)
    if match:
        # Chuyển dấu phẩy thành dấu chấm để Agent dễ tính toán
        return match.group(1).replace(',', '.')
    
    return "-"

def fetch_interest_rates(bank_name: str = "all", type_rate: str = "all") -> str:
    """
    Công cụ cào dữ liệu lãi suất từ webgia.com và trả về dạng CSV chuẩn hóa.
    - bank_name: Tên ngân hàng (VD: 'VPBank') hoặc truyền 'all' để lấy tất cả.
    """
    url = "https://webgia.com/lai-suat/"
    
    # GIẢ LẬP TRÌNH DUYỆT 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"Lỗi kết nối trang web: HTTP {response.status_code}"
            
        tables = pd.read_html(io.StringIO(response.text))
        
        if not tables:
            return "Lỗi: Không tìm thấy bất kỳ bảng nào trên trang web."
            
        # Tìm bảng lãi suất (bảng Tại quầy thường là bảng đầu tiên có đủ 10 cột, hoặc bảng thứ 2 là bảng Online)
        target_table = None
        for df in tables:
            if len(df.columns) >= 8: # Bảng chuẩn phải có từ 8 cột kỳ hạn trở lên
                target_table = df
                break
                
        if target_table is None:
            return "Lỗi: Không tìm thấy bảng lãi suất có cấu trúc chuẩn."
            
        df = target_table.copy()
        
        # Sửa lại tên cột cho phẳng (Xóa MultiIndex nếu Webgia dùng header 2 tầng)
        if isinstance(df.columns, pd.MultiIndex):
            # Lấy dòng thứ 2 (chứa số tháng) làm header
            df.columns = [str(col[-1]).strip() for col in df.columns]
        else:
            df.columns = [str(col).strip() for col in df.columns]
        
        # Đổi tên cột đầu tiên thành Ngân hàng cho dễ hiểu
        cols = list(df.columns)
        cols[0] = "Ngan_hang"
        df.columns = cols
        
        # Làm sạch dữ liệu các cột kỳ hạn
        for col in df.columns[1:]:
            df[col] = df[col].apply(extract_number)
        
        # Lọc ngân hàng
        if bank_name.lower() != "all":
            # Xóa chữ rác trong chính cột tên Ngân hàng nếu có
            df["Ngan_hang"] = df["Ngan_hang"].astype(str).apply(lambda x: re.sub(r'(webgia\.com|web giá|xem tại)', '', x, flags=re.IGNORECASE).strip())
            
            df = df[df["Ngan_hang"].str.contains(bank_name, case=False, na=False)]
            if df.empty:
                return f"Lỗi: Không tìm thấy dữ liệu cho ngân hàng {bank_name}."
                
        return df.to_csv(index=False)
        
    except Exception as e:
        return f"Lỗi khi cào dữ liệu: {str(e)}"

# Cấu hình Tool Spec
BANK_SCRAPE_TOOL = {
    "name": "fetch_interest_rates",
    "description": "Lấy bảng tổng hợp lãi suất từ WebGia dạng CSV. Truyền bank_name='all' để lấy toàn bộ, hoặc tên riêng (VD: 'MBBank').",
    "function": fetch_interest_rates
}

# ========================================================
# CODE TEST
# ========================================================
if _name_ == "_main_":
    print("=== BẮT ĐẦU TEST CÔNG CỤ TỪ WEBGIA ===")
    
    csv_string = fetch_interest_rates(bank_name="all")
    
    if not csv_string.startswith("Lỗi"):
        df_view = pd.read_csv(io.StringIO(csv_string))
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print("\n>> 10 NGÂN HÀNG ĐẦU TIÊN (ĐÃ LỌC SẠCH RÁC):\n")
        print(df_view.head(10))
        
        print("\n>> TÌM THỬ AGRIBANK:\n")
        print(fetch_interest_rates(bank_name="Agribank"))
    else:
        print(csv_string)
        
    print("\n=== HOÀN THÀNH TEST ===")
webgia.com
16:01
Thưởng
import pandas as pd
import polars as pl
import io
import re
from playwright.sync_api import sync_playwright

def extract_number(text):
    """Hàm lọc số chuẩn hóa và chia cho 100"""
    text_str = str(text).strip().lower()
    if pd.isna(text) or text_str in ['-', '', 'nan', 'none']:
        return "-"
        
    text_str = text_str.replace("web giá", "").replace("webgiá.com", "").replace("webgia.com", "")
    text_str = text_str.replace("xem tại", "").strip()

    match = re.search(r"(\d+[\.,]\d+|\d+)", text_str)
    if match:
        num_str = match.group(1).replace(',', '.')
        try:
            val = float(num_str) / 100
            return str(round(val, 2))  # Return string để match với return_dtype=pl.Utf8
        except ValueError:
            return "-"
    return "-"

def process_table(pd_df, hinh_thuc):
    """Hàm phụ trợ xử lý từng bảng đơn lẻ sử dụng Polars"""
    
    # 1. Làm phẳng tiêu đề bằng Pandas trước khi nạp vào Polars
    if isinstance(pd_df.columns, pd.MultiIndex):
        pd_df.columns = [str(col[-1]).strip() for col in pd_df.columns]
    else:
        pd_df.columns = [str(col).strip() for col in pd_df.columns]
    
    cols = list(pd_df.columns)
    cols[0] = "Ngan_hang"
    pd_df.columns = cols
    
    # 2. Chuyển tất cả cột sang string và tạo Polars từ dict (tránh pyarrow)
    data_dict = {col: pd_df[col].astype(str).tolist() for col in pd_df.columns}
    df = pl.DataFrame(data_dict)
    
    # 3. Thêm cột Hình thức gửi vào vị trí thứ 2
    df = df.insert_column(1, pl.lit(hinh_thuc).alias("Hinh_thuc"))
    
    # 4. Dọn dẹp số liệu bằng hàm apply của Polars
    term_cols = df.columns[2:] # Các cột từ thứ 3 trở đi là kỳ hạn
    
    # Áp dụng hàm trích xuất số cho từng cột kỳ hạn
    for col_name in term_cols:
         df = df.with_columns(
             pl.col(col_name).map_elements(extract_number, return_dtype=pl.Utf8)
         )
         
    return df

def fetch_interest_rates(bank_name: str = "all", type_rate: str = "all") -> str:
    """
    Công cụ cào dữ liệu từ webgia.com.
    Xử lý dữ liệu bằng sức mạnh của Polars.
    """
    url = "https://webgia.com/lai-suat/"
    
    try:
        # Cào HTML bằng Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
            page.goto(url, wait_until="networkidle", timeout=30000)
            html_source = page.content()
            browser.close()
            
        # Vẫn dùng Pandas read_html vì nó phân tích bảng HTML tốt nhất
        tables = pd.read_html(io.StringIO(html_source))
        
        if not tables:
            return "Lỗi: Không tìm thấy bảng nào."
            
        valid_tables = [df for df in tables if len(df.columns) >= 8]
        
        if len(valid_tables) == 0:
            return "Lỗi: Không tìm thấy bảng lãi suất chuẩn."
            
        processed_dfs = []
        
        if len(valid_tables) > 0:
            df_tai_quay = process_table(valid_tables[0].copy(), "Tai_quay")
            processed_dfs.append(df_tai_quay)
            
        if len(valid_tables) > 1:
            df_online = process_table(valid_tables[1].copy(), "Online")
            processed_dfs.append(df_online)
            
        # Gộp tất cả các bảng lại thành một bằng Polars
        # how="diagonal" tương đương với ignore_index=True và lấp khoảng trống của Pandas
        final_df = pl.concat(processed_dfs, how="diagonal")
        
        # Lấp đầy null bằng dấu "-"
        final_df = final_df.fill_null("-")
        
        # Lọc theo hình thức
        if type_rate.lower() == "tai_quay":
            final_df = final_df.filter(pl.col("Hinh_thuc") == "Tai_quay")
        elif type_rate.lower() == "online":
            final_df = final_df.filter(pl.col("Hinh_thuc") == "Online")
            
        # Lọc theo ngân hàng
        if bank_name.lower() != "all":
            # Xóa rác trong tên ngân hàng
            final_df = final_df.with_columns(
                pl.col("Ngan_hang").str.replace_all(r"(?i)(webgia\.com|web giá|xem tại)", "").str.strip_chars()
            )
            
            # Lọc chứa từ khóa (không phân biệt hoa thường)
            final_df = final_df.filter(
                pl.col("Ngan_hang").str.to_lowercase().str.contains(bank_name.lower())
            )
            
            if final_df.height == 0: # height trong Polars tương đương len() của Pandas
                return f"Lỗi: Không tìm thấy dữ liệu cho ngân hàng {bank_name}."
                
        # Xuất ra CSV dạng chuỗi
        return final_df.write_csv()
        
    except Exception as e:
        return f"Lỗi khi cào bằng Playwright/Polars: {str(e)}"

# Cấu hình Tool Spec
BANK_SCRAPE_TOOL = {
    "name": "fetch_interest_rates",
    "description": "Lấy bảng tổng hợp lãi suất từ WebGia dạng CSV. Truyền bank_name='all' để lấy toàn bộ ngân hàng. Truyền type_rate='all' để lấy cả online và tại quầy, hoặc truyền 'tai_quay', 'online' để lọc.",
    "function": fetch_interest_rates
}

# ========================================================
# CODE TEST
# ========================================================
if _name_ == "_main_":
    print("=== BẮT ĐẦU TEST CÔNG CỤ (PLAYWRIGHT + POLARS) ===\n")
    print("Đang cào và giải mã dữ liệu... \n")
    
    csv_string = fetch_interest_rates(bank_name="all", type_rate="all")
    
    if not csv_string.startswith("Lỗi"):
        # Đọc lại CSV bằng Polars để hiển thị
        df_view = pl.read_csv(io.StringIO(csv_string))
        
        # Cấu hình Polars để in ra toàn bộ bảng đẹp mắt
        pl.Config.set_tbl_rows(100) # In tối đa 100 dòng
        pl.Config.set_tbl_cols(20)  # In tối đa 20 cột
        
        print(">> BẢNG DỮ LIỆU LÃI SUẤT TỔNG HỢP:\n")
        print(df_view)
        
    else:
        print(csv_string)
        
    print("\n=== HOÀN THÀNH TEST ===")