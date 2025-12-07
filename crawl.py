import requests
from bs4 import BeautifulSoup
import time

# --- CẤU HÌNH ---
SIZES = [7, 9, 13, 20]      # Các kích thước cần lấy
SAMPLES_PER_SIZE = 5        # Số lượng bài cần lấy mỗi size
START_INDEX = 21            # Tên file bắt đầu từ input-21.txt
BASE_URL = "https://menneske.no/hashi/{}x{}/eng/showpuzzle.html?number={}"

def get_puzzle_matrix(size, number):
    url = BASE_URL.format(size, size, number)
    try:
        # Giả lập trình duyệt
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm bảng câu đố
        puzzle_div = soup.find('div', class_='hashi')
        if not puzzle_div: return None
        table = puzzle_div.find('table')
        if not table: return None

        matrix = []
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if not cells: continue
            
            row_data = []
            for cell in cells:
                txt = cell.get_text(strip=True)
                # Nếu là số thì lấy, không thì gán bằng 0
                if txt.isdigit():
                    row_data.append(txt)
                else:
                    row_data.append('0')
            matrix.append(row_data)

        # Kiểm tra kích thước ma trận có đúng size không
        if len(matrix) != size:
            return None
        return matrix

    except Exception as e:
        print(f"Lỗi kết nối: {e}")
        return None

def main():
    file_counter = START_INDEX
    
    for size in SIZES:
        print(f"--- Đang lấy size {size}x{size} ---")
        count = 0
        puzzle_num = 1 # Bắt đầu từ bài số 1
        
        while count < SAMPLES_PER_SIZE:
            matrix = get_puzzle_matrix(size, puzzle_num)
            
            if matrix:
                filename = f"Inputs/input-{file_counter}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    for row in matrix:
                        f.write(", ".join(row) + "\n")
                
                print(f"   [OK] Đã lưu {filename} (Puzzle #{puzzle_num})")
                file_counter += 1
                count += 1
            else:
                print(f"   [LỖI] Bỏ qua Puzzle #{puzzle_num}")
            
            # Tăng số thứ tự để lấy bài khác nhau cho lần lặp sau
            puzzle_num += 1
            time.sleep(0.5) # Nghỉ nhẹ

    print(f"\nHOÀN TẤT! File cuối cùng là input-{file_counter - 1}.txt")

if __name__ == "__main__":
    main()