import requests
import urllib3
import sys
import time
from urllib.parse import urlparse, parse_qs, urlencode

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ValkyrieZeroDayEngine:
    def __init__(self, target_url):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({'User-Agent': 'Valkyrie-ZeroDay-Engine/3.0'})

    def banner(self):
        print("="*80)
        print(" VALKYRIE ZERO-DAY ENGINE v3.0 | HEURISTIC & ANOMALY DETECTION ENGINE")
        print("="*80)

    def analyze_behavioral_anomaly(self):
        """
        TÍNH NĂNG ĐỘT PHÁ: Phân tích hành vi bất thường (Anomaly Detection)
        Dùng để săn Zero-day bằng cách đo lường độ lệch chuẩn của phản hồi hệ thống.
        """
        print("\n[*] Khởi chạy bộ lọc phân tích hành vi bất thường để săn tìm Zero-day...")
        
        # Bước 1: Lấy mẫu phản hồi chuẩn của hệ thống (Baseline)
        try:
            start_time = time.time()
            baseline_res = self.session.get(self.target_url, timeout=5)
            baseline_time = time.time() - start_time
            baseline_size = len(baseline_res.text)
            
            print(f"[+] Phản hồi tiêu chuẩn (Baseline): Thời gian: {baseline_time:.4f}s | Kích thước: {baseline_size} bytes")
        except Exception as e:
            print(f"[-] Không thể thiết lập phản hồi tiêu chuẩn: {e}")
            return

        # Bước 2: Nhồi các biến dị dữ liệu logic (Data Mutation) để tìm lỗi xử lý ngầm (Unhandled Exceptions)
        # Các payload này không mang chữ ký của lỗi cụ thể nào, mà mang cấu trúc bẻ gãy logic dữ liệu
        mutations = {
            "Array Mutation": {"id[]": "vzk"},
            "Null Byte Mutation": {"id": "%00"},
            "Unicode/Overflow Mutation": {"id": "A" * 1000 + "𝔡𝔢𝔞𝔡𝔟𝔢𝔢𝔣"},
            "Type Confusion": {"id": "true"}
        }

        parsed_url = urlparse(self.target_url)
        base_endpoint = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

        for mutation_name, payload in mutations.items():
            test_url = f"{base_endpoint}?{urlencode(payload)}"
            try:
                start_test = time.time()
                test_res = self.session.get(test_url, timeout=5)
                test_time = time.time() - start_test
                test_size = len(test_res.text)

                # Thuật toán so sánh độ lệch chuẩn để phát hiện Zero-day
                time_diff = abs(test_time - baseline_time)
                size_diff = abs(test_size - baseline_size)

                print(f"\n[*] Kiểm thử biến dị: [{mutation_name}] -> {test_url}")

                # Tiêu chí 1: Trả về mã lỗi hệ thống 500 nhưng không có giao diện lỗi chuẩn
                if test_res.status_code == 500:
                    print(f"[-] ĐIỂM TIỀM TÀNG ZERO-DAY: Máy chủ gặp lỗi xử lý ngầm (HTTP 500 Internal Error).")
                    print(f"    [!] Cơ chế: Mã nguồn ứng dụng không bắt được kiểu dữ liệu biến dị này.")
                
                # Tiêu chí 2: Trễ thời gian bất thường (Ứng dụng bị kẹt hoặc xử lý vòng lặp vô hạn)
                elif time_diff > 3.0:
                    print(f"[-] ĐIỂM TIỀM TÀNG ZERO-DAY: Phát hiện độ trễ thời gian bất thường ({test_time:.2f}s).")
                    print(f"    [!] Cơ chế: Có khả năng xảy ra lỗi nghẽn thuật toán hoặc vòng lặp tài nguyên không kiểm soát.")

                # Tiêu chí 3: Cấu trúc trang web thay đổi đột ngột (Kích thước lệch quá lớn)
                elif size_diff > (baseline_size * 0.5):
                    print(f"[-] ĐIỂM TIỀM TÀNG ZERO-DAY: Cấu trúc trang phản hồi bị thay đổi đột ngột ({test_size} bytes).")
                    print(f"    [!] Cơ chế: Biến dị dữ liệu làm rò rỉ luồng xử lý hoặc cấu trúc dữ liệu thô ra ngoài.")
                else:
                    print(f"[+] Kết quả biến dị nằm trong vùng an toàn xử lý.")

            except requests.exceptions.Timeout:
                print(f"[-] ĐIỂM TIỀM TÀNG ZERO-DAY: Ứng dụng bị sập ứng cứu hoặc rơi vào trạng thái Denial of Service (Timeout)!")
            except Exception:
                continue

    def run(self):
        self.banner()
        self.analyze_behavioral_anomaly()
        print("\n[+] Tiến trình phân tích Heuristic hoàn tất.")
        print("="*80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[*] python3 valkyrie_zde.py <URL>")
        sys.exit(1)
    
    scanner = ValkyrieZeroDayEngine(sys.argv[1])
    scanner.run()
